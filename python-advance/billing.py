
"""
find_active_regions.py
-----------------------
Finds all AWS regions where a customer:
  1. Has been BILLED for any resources (via AWS Cost Explorer)
  2. Has any ACTIVE RESOURCES (via AWS Resource Explorer or per-service scans)

APIs Used:
  - Cost Explorer  : get_cost_and_usage         → billed regions
  - EC2            : describe_regions            → all enabled regions
  - Resource Explorer: search (if enabled)       → resources across all regions
  - Per-service fallback scans across all regions
"""

import boto3
import json
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from botocore.exceptions import ClientError, EndpointConnectionError

# ── Config ────────────────────────────────────────────────────────────────────
LOOKBACK_MONTHS = 2        # How many months back to check billing
OUTPUT_FILE     = "active_regions.json"
# ─────────────────────────────────────────────────────────────────────────────


def get_all_enabled_regions() -> list[str]:
    """Return all regions currently enabled for this account."""
    ec2 = boto3.client("ec2", region_name="us-east-1")
    resp = ec2.describe_regions(AllRegions=False)
    return sorted(r["RegionName"] for r in resp["Regions"])


# ── Method 1: Cost Explorer ───────────────────────────────────────────────────

def get_billed_regions(months: int = LOOKBACK_MONTHS) -> dict[str, float]:
    """
    Uses AWS Cost Explorer to find every region the account was billed in
    over the last `months` months.

    Returns: { "us-east-1": 123.45, "eu-west-1": 67.89, ... }
    """
    ce = boto3.client("ce", region_name="us-east-1")

    end   = datetime.now(timezone.utc).date().replace(day=1)  # first of this month
    start = (end - relativedelta(months=months))               # N months ago

    print(f"  Querying Cost Explorer from {start} to {end} ...")

    billed = {}
    try:
        next_token = None
        while True:
            kwargs = dict(
                TimePeriod={"Start": str(start), "End": str(end)},
                Granularity="MONTHLY",
                Metrics=["UnblendedCost"],
                GroupBy=[{"Type": "DIMENSION", "Key": "REGION"}],
            )
            if next_token:
                kwargs["NextPageToken"] = next_token

            resp = ce.get_cost_and_usage(**kwargs)

            for result in resp["ResultsByTime"]:
                for group in result["Groups"]:
                    region = group["Keys"][0]
                    cost   = float(group["Metrics"]["UnblendedCost"]["Amount"])
                    if region and region != "NoRegion" and cost > 0:
                        billed[region] = round(billed.get(region, 0) + cost, 4)

            next_token = resp.get("NextPageToken")
            if not next_token:
                break
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code in ("AccessDeniedException", "OptInRequired"):
            print(f"  ⚠ Cost Explorer not available: {code}")
        else:
            raise

    return billed


# ── Method 2: Resource Explorer v2 ───────────────────────────────────────────

def get_regions_via_resource_explorer() -> set[str]:
    """
    Uses AWS Resource Explorer (if enabled) to find regions that have resources.
    Resource Explorer aggregates across all regions from a single API call.
    """
    regions = set()
    try:
        re2 = boto3.client("resource-explorer-2", region_name="us-east-1")
        paginator = re2.get_paginator("search")
        print("  Querying AWS Resource Explorer ...")
        for page in paginator.paginate(QueryString=""):
            for resource in page.get("Resources", []):
                r = resource.get("Region")
                if r:
                    regions.add(r)
    except ClientError as e:
        code = e.response["Error"]["Code"]
        print(f"  ⚠ Resource Explorer not available ({code}), falling back to per-service scan.")
    except Exception as e:
        print(f"  ⚠ Resource Explorer error: {e}")
    return regions


# ── Method 3: Per-service fallback scan ──────────────────────────────────────

RESOURCE_CHECKS = [
    # (service, method, result_key, count_field_or_len)
    # Each tuple: boto3 client name, list method, top-level key in response
    ("ec2",            "describe_instances",          "Reservations"),
    ("ec2",            "describe_volumes",            "Volumes"),
    ("ec2",            "describe_vpcs",               "Vpcs"),
    ("rds",            "describe_db_instances",       "DBInstances"),
    ("lambda_",        "list_functions",              "Functions"),
    ("elbv2",          "describe_load_balancers",     "LoadBalancers"),
    ("s3",             None,                          None),    # global, handled separately
    ("eks",            "list_clusters",               "clusters"),
    ("ecs",            "list_clusters",               "clusterArns"),
    ("elasticache",    "describe_cache_clusters",     "CacheClusters"),
    ("es",             "list_domain_names",           "DomainNames"),
    ("sqs",            "list_queues",                 "QueueUrls"),
    ("sns",            "list_topics",                 "Topics"),
    ("dynamodb",       "list_tables",                 "TableNames"),
    ("cloudformation", "list_stacks",                 "StackSummaries"),
    ("kinesis",        "list_streams",                "StreamNames"),
    ("redshift",       "describe_clusters",           "Clusters"),
    ("glue",           "get_databases",               "DatabaseList"),
]


def check_region_has_resources(region: str) -> tuple[bool, list[str]]:
    """
    Scans multiple AWS services in a given region.
    Returns (has_resources: bool, list of services that have resources).
    """
    found_services = []

    for service, method, key in RESOURCE_CHECKS:
        if service == "s3":
            continue  # S3 is global, handled separately
        try:
            client_name = service.rstrip("_")  # lambda_ → lambda
            client = boto3.client(client_name, region_name=region)
            func   = getattr(client, method)

            # Some APIs need special kwargs
            kwargs = {}
            if service == "cloudformation":
                kwargs = {"StackStatusFilter": [
                    "CREATE_COMPLETE", "UPDATE_COMPLETE", "ROLLBACK_COMPLETE",
                    "UPDATE_ROLLBACK_COMPLETE", "REVIEW_IN_PROGRESS"
                ]}
            elif service == "glue":
                kwargs = {"DatabaseInput": None} if False else {}

            resp  = func(**kwargs)
            items = resp.get(key, [])
            if items:
                found_services.append(client_name)

        except ClientError as e:
            code = e.response["Error"]["Code"]
            if code in ("AccessDeniedException", "AuthFailure",
                        "UnauthorizedOperation", "OptInRequired",
                        "SubscriptionRequiredException"):
                pass  # No access or not opted in — skip silently
        except (EndpointConnectionError, Exception):
            pass  # Region unreachable for this service

    return bool(found_services), found_services


def get_regions_via_service_scan(all_regions: list[str]) -> dict[str, list[str]]:
    """Scan every region for active resources. Returns {region: [services]}."""
    active = {}
    total  = len(all_regions)
    for i, region in enumerate(all_regions, 1):
        print(f"  [{i:>2}/{total}] Scanning {region} ...", end=" ", flush=True)
        has_resources, services = check_region_has_resources(region)
        if has_resources:
            active[region] = services
            print(f"✅ {', '.join(services)}")
        else:
            print("—")
    return active


# ── S3: Global service ────────────────────────────────────────────────────────

def get_s3_bucket_regions() -> dict[str, list[str]]:
    """S3 is a global service. Map each bucket to its region."""
    region_buckets: dict[str, list[str]] = {}
    try:
        s3 = boto3.client("s3", region_name="us-east-1")
        resp = s3.list_buckets()
        for bucket in resp.get("Buckets", []):
            name = bucket["Name"]
            try:
                loc  = s3.get_bucket_location(Bucket=name)
                region = loc["LocationConstraint"] or "us-east-1"
                region_buckets.setdefault(region, []).append(name)
            except ClientError:
                pass
    except ClientError as e:
        print(f"  ⚠ S3 scan error: {e.response['Error']['Code']}")
    return region_buckets


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  AWS Active Regions Finder")
    print("=" * 60)

    # Step 1: Get all enabled regions
    print("\n[1/4] Fetching all enabled regions ...")
    all_regions = get_all_enabled_regions()
    print(f"  Found {len(all_regions)} enabled regions.")

    # Step 2: Cost Explorer — billed regions
    print(f"\n[2/4] Checking Cost Explorer (last {LOOKBACK_MONTHS} months) ...")
    billed_regions = get_billed_regions()
    print(f"  Found {len(billed_regions)} billed region(s): {sorted(billed_regions)}")

    # Step 3: Resource Explorer (fast, single API)
    print("\n[3/4] Checking AWS Resource Explorer ...")
    re_regions = get_regions_via_resource_explorer()
    print(f"  Found {len(re_regions)} region(s) via Resource Explorer.")

    # Step 4: Per-service scan (thorough fallback)
    print("\n[4/4] Running per-service resource scan across all regions ...")
    service_regions = get_regions_via_service_scan(all_regions)

    # Step 5: S3 buckets
    print("\n[+] Scanning S3 buckets (global service) ...")
    s3_regions = get_s3_bucket_regions()
    print(f"  Found S3 buckets in: {sorted(s3_regions.keys())}")

    # ── Merge all sources ──────────────────────────────────────────────────────
    all_active = set(billed_regions) | re_regions | set(service_regions) | set(s3_regions)

    result = {
        "summary": {
            "total_active_regions": len(all_active),
            "active_regions": sorted(all_active),
        },
        "billed_regions": {
            r: {"total_cost_usd": billed_regions[r]} for r in sorted(billed_regions)
        },
        "resource_explorer_regions": sorted(re_regions),
        "service_scan": {
            r: service_regions[r] for r in sorted(service_regions)
        },
        "s3_bucket_regions": {
            r: s3_regions[r] for r in sorted(s3_regions)
        },
    }

    # ── Print summary ──────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  RESULTS SUMMARY")
    print("=" * 60)
    print(f"  Total active regions : {len(all_active)}")
    print(f"  Active regions       : {sorted(all_active)}")
    print(f"\n  Sources breakdown:")
    print(f"    • Cost Explorer      : {len(billed_regions)} region(s)")
    print(f"    • Resource Explorer  : {len(re_regions)} region(s)")
    print(f"    • Service scan       : {len(service_regions)} region(s)")
    print(f"    • S3 buckets         : {len(s3_regions)} region(s)")

    # ── Save to JSON ───────────────────────────────────────────────────────────
    with open(OUTPUT_FILE, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\n  Full results saved to: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()