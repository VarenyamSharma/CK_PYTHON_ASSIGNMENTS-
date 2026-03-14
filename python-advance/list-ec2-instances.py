import boto3
import csv
import sys
from botocore.exceptions import ClientError, EndpointResolutionError

OUTPUT_FILE = "ec2_instance_types.csv"


def get_all_regions(ec2_client):
    """Fetch all available EC2 regions."""
    response = ec2_client.describe_regions(AllRegions=False)
    return [r["RegionName"] for r in response["Regions"]]


def get_instance_types_for_region(region: str) -> list[str]:
    """Return a deduplicated list of EC2 instance types available in a region."""
    ec2 = boto3.client("ec2", region_name=region)
    instance_types = set()
    paginator = ec2.get_paginator("describe_instance_type_offerings")

    for page in paginator.paginate(LocationType="region"):
        for offering in page["InstanceTypeOfferings"]:
            instance_types.add(offering["InstanceType"])

    return sorted(instance_types)


def main():
    print("Fetching available AWS regions...")
    base_client = boto3.client("ec2", region_name="us-east-1")

    try:
        regions = get_all_regions(base_client)
    except ClientError as e:
        print(f"Error fetching regions: {e}")
        sys.exit(1)

    print(f"Found {len(regions)} regions. Collecting instance types...\n")

    rows = []
    for i, region in enumerate(regions, 1):
        print(f"[{i}/{len(regions)}] Processing region: {region}")
        try:
            instance_types = get_instance_types_for_region(region)
            for it in instance_types:
                rows.append({"region": region, "instance_type": it})
            print(f"  -> {len(instance_types)} unique instance types found")
        except (ClientError, EndpointResolutionError) as e:
            print(f"  -> Skipping {region}: {e}")

    print(f"\nWriting {len(rows)} rows to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["region", "instance_type"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done! Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()