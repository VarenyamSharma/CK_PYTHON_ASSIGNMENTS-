"""
aws_security_audit.py
----------------------
AWS Security Best Practices Audit Script

Checks:
  1. IAM roles with overly permissive policies (AdministratorAccess)
  2. MFA status for all IAM users
  3. Security groups with public access on ports 22, 80, 443
  4. Unused EC2 key pairs

Output: 4 CSV files
  - iam_overpermissive_roles.csv
  - iam_mfa_status.csv
  - security_group_public_access.csv
  - unused_keypairs.csv
"""

import boto3
import csv
import json
from botocore.exceptions import ClientError
from datetime import datetime, timezone

# ── Config ─────────────────────────────────────────────────────────────────────
SENSITIVE_PORTS         = [22, 80, 443, 3306, 5432, 1433, 27017, 6379]
PUBLIC_CIDRS            = ["0.0.0.0/0", "::/0"]
OVERPERMISSIVE_ACTIONS  = ["*", "AdministratorAccess"]

OUTPUT_ROLES_CSV        = "iam_overpermissive_roles.csv"
OUTPUT_MFA_CSV          = "iam_mfa_status.csv"
OUTPUT_SG_CSV           = "security_group_public_access.csv"
OUTPUT_KEYPAIRS_CSV     = "unused_keypairs.csv"

BOLD   = "\033[1m"
RED    = "\033[91m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
CYAN   = "\033[96m"
RESET  = "\033[0m"

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

# ── Helper: Write CSV ──────────────────────────────────────────────────────────

def write_csv(filepath: str, fieldnames: list[str], rows: list[dict]):
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  {GREEN}✅ Saved → {filepath}  ({len(rows)} row(s)){RESET}")


# ══════════════════════════════════════════════════════════════════════════════
# CHECK 1: IAM Roles with Overly Permissive Policies
# ══════════════════════════════════════════════════════════════════════════════

def check_iam_overpermissive_roles(iam_client) -> list[dict]:
    """
    Lists all IAM roles and their attached/inline policies.
    Flags any role that has AdministratorAccess or Action: * in any policy.

    CSV: IAMRoleName, PolicyName, PolicyType, PermissiveAction
    """
    print(f"\n{CYAN}[CHECK 1] Scanning IAM roles for overly permissive policies...{RESET}")
    flagged = []

    try:
        role_paginator = iam_client.get_paginator("list_roles")
        roles = []
        for page in role_paginator.paginate():
            roles.extend(page["Roles"])
        print(f"  Found {len(roles)} IAM role(s).")

        for role in roles:
            role_name = role["RoleName"]

            # ── Attached managed policies ──────────────────────────────────────
            try:
                att_paginator = iam_client.get_paginator("list_attached_role_policies")
                for page in att_paginator.paginate(RoleName=role_name):
                    for policy in page["AttachedPolicies"]:
                        policy_name = policy["PolicyName"]
                        policy_arn  = policy["PolicyArn"]

                        # AdministratorAccess by name
                        if "AdministratorAccess" in policy_name:
                            flagged.append({
                                "IAMRoleName":       role_name,
                                "PolicyName":        policy_name,
                                "PolicyType":        "Managed (Attached)",
                                "PermissiveAction":  "AdministratorAccess",
                                "PolicyArn":         policy_arn,
                            })
                            continue

                        # Inspect policy document for Action: *
                        try:
                            version_id = iam_client.get_policy(
                                PolicyArn=policy_arn
                            )["Policy"]["DefaultVersionId"]
                            doc = iam_client.get_policy_version(
                                PolicyArn=policy_arn,
                                VersionId=version_id
                            )["PolicyVersion"]["Document"]

                            permissive = _find_wildcard_actions(doc)
                            if permissive:
                                flagged.append({
                                    "IAMRoleName":       role_name,
                                    "PolicyName":        policy_name,
                                    "PolicyType":        "Managed (Attached)",
                                    "PermissiveAction":  ", ".join(permissive),
                                    "PolicyArn":         policy_arn,
                                })
                        except ClientError:
                            pass

            except ClientError:
                pass

            # ── Inline policies ────────────────────────────────────────────────
            try:
                inline_paginator = iam_client.get_paginator("list_role_policies")
                for page in inline_paginator.paginate(RoleName=role_name):
                    for policy_name in page["PolicyNames"]:
                        try:
                            doc = iam_client.get_role_policy(
                                RoleName=role_name,
                                PolicyName=policy_name
                            )["PolicyDocument"]

                            permissive = _find_wildcard_actions(doc)
                            if permissive:
                                flagged.append({
                                    "IAMRoleName":       role_name,
                                    "PolicyName":        policy_name,
                                    "PolicyType":        "Inline",
                                    "PermissiveAction":  ", ".join(permissive),
                                    "PolicyArn":         "N/A (inline)",
                                })
                        except ClientError:
                            pass
            except ClientError:
                pass

    except ClientError as e:
        print(f"  {RED}⚠ IAM error: {e.response['Error']['Code']}{RESET}")

    print(f"  {YELLOW}Flagged {len(flagged)} overly permissive role-policy pair(s).{RESET}")
    return flagged


def _find_wildcard_actions(policy_doc: dict) -> list[str]:
    """Return list of wildcard/overpermissive actions found in a policy document."""
    found = []
    statements = policy_doc.get("Statement", [])
    if isinstance(statements, dict):
        statements = [statements]

    for stmt in statements:
        if stmt.get("Effect") != "Allow":
            continue
        actions = stmt.get("Action", [])
        if isinstance(actions, str):
            actions = [actions]
        for action in actions:
            if action == "*" or action.endswith(":*"):
                if action not in found:
                    found.append(action)
    return found


# ══════════════════════════════════════════════════════════════════════════════
# CHECK 2: IAM Users MFA Status
# ══════════════════════════════════════════════════════════════════════════════

def check_iam_mfa_status(iam_client) -> list[dict]:
    """
    Lists all IAM users and checks if MFA is enabled.

    CSV: IAMUserName, MFAEnabled, MFADeviceType, PasswordLastUsed, AccountAge_Days
    """
    print(f"\n{CYAN}[CHECK 2] Checking MFA status for all IAM users...{RESET}")
    rows = []

    try:
        user_paginator = iam_client.get_paginator("list_users")
        users = []
        for page in user_paginator.paginate():
            users.extend(page["Users"])
        print(f"  Found {len(users)} IAM user(s).")

        for user in users:
            username       = user["UserName"]
            created        = user.get("CreateDate")
            pwd_last_used  = user.get("PasswordLastUsed")
            age_days       = (datetime.now(timezone.utc) - created).days if created else "N/A"
            pwd_str        = pwd_last_used.strftime("%Y-%m-%d") if pwd_last_used else "Never"

            # Check MFA devices
            mfa_devices = []
            try:
                mfa_resp = iam_client.list_mfa_devices(UserName=username)
                mfa_devices = mfa_resp.get("MFADevices", [])
            except ClientError:
                pass

            mfa_enabled = len(mfa_devices) > 0
            device_types = ", ".join(
                set(d.get("SerialNumber", "").split(":")[4] if "arn" in d.get("SerialNumber","")
                    else ("Virtual" if "mfa" in d.get("SerialNumber","").lower() else "Hardware")
                    for d in mfa_devices)
            ) if mfa_devices else "None"

            rows.append({
                "IAMUserName":      username,
                "MFAEnabled":       mfa_enabled,
                "MFADeviceType":    device_types,
                "PasswordLastUsed": pwd_str,
                "AccountAge_Days":  age_days,
            })

            status_icon = GREEN + "✅" + RESET if mfa_enabled else RED + "⚠ " + RESET
            print(f"  {status_icon} {username:35s} MFA: {str(mfa_enabled):<5}  Device: {device_types}")

    except ClientError as e:
        print(f"  {RED}⚠ IAM error: {e.response['Error']['Code']}{RESET}")

    mfa_off = sum(1 for r in rows if not r["MFAEnabled"])
    print(f"  {YELLOW}{mfa_off} user(s) have MFA disabled.{RESET}")
    return rows


# ══════════════════════════════════════════════════════════════════════════════
# CHECK 3: Security Groups with Public Access
# ══════════════════════════════════════════════════════════════════════════════

def check_security_groups_public_access(ec2_client) -> list[dict]:
    """
    Checks all security groups for inbound rules allowing 0.0.0.0/0 or ::/0
    on sensitive ports (22, 80, 443, 3306, 5432, etc.)

    CSV: SGName, SGID, VpcId, Port, Protocol, AllowedIP, RuleDescription
    """
    print(f"\n{CYAN}[CHECK 3] Checking security groups for public access...{RESET}")
    flagged = []

    try:
        paginator = ec2_client.get_paginator("describe_security_groups")
        sgs = []
        for page in paginator.paginate():
            sgs.extend(page["SecurityGroups"])
        print(f"  Found {len(sgs)} security group(s).")

        for sg in sgs:
            sg_id   = sg["GroupId"]
            sg_name = sg.get("GroupName", "N/A")
            vpc_id  = sg.get("VpcId", "N/A")

            for rule in sg.get("IpPermissions", []):
                protocol   = rule.get("IpProtocol", "N/A")
                from_port  = rule.get("FromPort", 0)
                to_port    = rule.get("ToPort", 65535)

                # Collect all public CIDRs in this rule
                public_cidrs_found = []
                for ipv4 in rule.get("IpRanges", []):
                    if ipv4.get("CidrIp") in PUBLIC_CIDRS:
                        public_cidrs_found.append(ipv4["CidrIp"])
                for ipv6 in rule.get("Ipv6Ranges", []):
                    if ipv6.get("CidrIpv6") in PUBLIC_CIDRS:
                        public_cidrs_found.append(ipv6["CidrIpv6"])

                if not public_cidrs_found:
                    continue

                # protocol -1 means ALL traffic
                if protocol == "-1":
                    for cidr in public_cidrs_found:
                        flagged.append({
                            "SGName":          sg_name,
                            "SGID":            sg_id,
                            "VpcId":           vpc_id,
                            "Port":            "ALL",
                            "Protocol":        "ALL",
                            "AllowedIP":       cidr,
                            "RuleDescription": "All traffic allowed from public",
                        })
                    continue

                # Check each sensitive port range
                for port in SENSITIVE_PORTS:
                    if from_port <= port <= to_port:
                        for cidr in public_cidrs_found:
                            flagged.append({
                                "SGName":          sg_name,
                                "SGID":            sg_id,
                                "VpcId":           vpc_id,
                                "Port":            port,
                                "Protocol":        protocol.upper(),
                                "AllowedIP":       cidr,
                                "RuleDescription": f"Port {port} open to public internet",
                            })

    except ClientError as e:
        print(f"  {RED}⚠ EC2 error: {e.response['Error']['Code']}{RESET}")

    print(f"  {YELLOW}Found {len(flagged)} public-access rule(s) across security groups.{RESET}")
    return flagged


# ══════════════════════════════════════════════════════════════════════════════
# CHECK 4: Unused EC2 Key Pairs
# ══════════════════════════════════════════════════════════════════════════════

def check_unused_keypairs(ec2_client) -> list[dict]:
    """
    Lists all EC2 key pairs and checks which ones are NOT attached to any instance.

    CSV: KeyPairName, KeyPairId, CreatedDate, UsedByInstances, Status
    """
    print(f"\n{CYAN}[CHECK 4] Checking for unused EC2 key pairs...{RESET}")
    rows = []

    try:
        # Get all key pairs
        kp_resp   = ec2_client.describe_key_pairs(IncludePublicKey=False)
        key_pairs = kp_resp.get("KeyPairs", [])
        print(f"  Found {len(key_pairs)} key pair(s).")

        # Get all key names in use across all instances (any state)
        in_use_keys = set()
        inst_paginator = ec2_client.get_paginator("describe_instances")
        for page in inst_paginator.paginate():
            for reservation in page["Reservations"]:
                for inst in reservation["Instances"]:
                    kn = inst.get("KeyName")
                    if kn:
                        in_use_keys.add(kn)

        print(f"  Key pairs in use by instances: {len(in_use_keys)}")

        for kp in key_pairs:
            kp_name    = kp["KeyName"]
            kp_id      = kp.get("KeyPairId", "N/A")
            created    = kp.get("CreateTime")
            created_str = created.strftime("%Y-%m-%d") if created else "N/A"
            in_use     = kp_name in in_use_keys
            status     = "IN USE" if in_use else "UNUSED"

            rows.append({
                "KeyPairName":      kp_name,
                "KeyPairId":        kp_id,
                "CreatedDate":      created_str,
                "UsedByInstances":  in_use,
                "Status":           status,
            })

            icon = GREEN + "✅" + RESET if in_use else RED + "⚠ " + RESET
            print(f"  {icon} {kp_name:40s} → {status}")

    except ClientError as e:
        print(f"  {RED}⚠ EC2 error: {e.response['Error']['Code']}{RESET}")

    unused = sum(1 for r in rows if r["Status"] == "UNUSED")
    print(f"  {YELLOW}{unused} unused key pair(s) found.{RESET}")
    return rows


# ── Summary Report ─────────────────────────────────────────────────────────────

def print_summary(roles_flagged, mfa_rows, sg_flagged, kp_rows):
    divider = "=" * 65
    mfa_off  = sum(1 for r in mfa_rows   if not r["MFAEnabled"])
    kp_unused = sum(1 for r in kp_rows   if r["Status"] == "UNUSED")

    print(f"\n{BOLD}{divider}")
    print("        🔐 AWS SECURITY AUDIT — SUMMARY REPORT")
    print(f"{divider}{RESET}")
    print(f"  Report Time  : {NOW}\n")

    print(f"  {'CHECK':<45} {'FINDINGS':>8}")
    print(f"  {'-'*55}")
    print(f"  {'1. IAM Roles with Overly Permissive Policies':<45} {RED if roles_flagged else GREEN}{len(roles_flagged):>8}{RESET}")
    print(f"  {'2. IAM Users with MFA Disabled':<45} {RED if mfa_off else GREEN}{mfa_off:>8}{RESET}")
    print(f"  {'3. Security Groups with Public Access Rules':<45} {RED if sg_flagged else GREEN}{len(sg_flagged):>8}{RESET}")
    print(f"  {'4. Unused EC2 Key Pairs':<45} {RED if kp_unused else GREEN}{kp_unused:>8}{RESET}")
    print(f"  {'-'*55}")

    print(f"\n  📁 Output Files:")
    print(f"     • {OUTPUT_ROLES_CSV}")
    print(f"     • {OUTPUT_MFA_CSV}")
    print(f"     • {OUTPUT_SG_CSV}")
    print(f"     • {OUTPUT_KEYPAIRS_CSV}")
    print(f"\n{BOLD}{divider}{RESET}\n")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print(f"{BOLD}{'=' * 65}")
    print("     🔐 AWS Security Best Practices Audit")
    print(f"{'=' * 65}{RESET}")
    print(f"  Started : {NOW}")

    session    = boto3.Session()
    iam_client = session.client("iam")
    ec2_client = session.client("ec2")

    # ── Run all 4 checks ──────────────────────────────────────────────────────
    roles_flagged = check_iam_overpermissive_roles(iam_client)
    mfa_rows      = check_iam_mfa_status(iam_client)
    sg_flagged    = check_security_groups_public_access(ec2_client)
    kp_rows       = check_unused_keypairs(ec2_client)

    # ── Write CSVs ────────────────────────────────────────────────────────────
    print(f"\n{CYAN}[OUTPUT] Writing CSV reports...{RESET}")

    write_csv(
        OUTPUT_ROLES_CSV,
        ["IAMRoleName", "PolicyName", "PolicyType", "PermissiveAction", "PolicyArn"],
        roles_flagged,
    )

    write_csv(
        OUTPUT_MFA_CSV,
        ["IAMUserName", "MFAEnabled", "MFADeviceType", "PasswordLastUsed", "AccountAge_Days"],
        mfa_rows,
    )

    write_csv(
        OUTPUT_SG_CSV,
        ["SGName", "SGID", "VpcId", "Port", "Protocol", "AllowedIP", "RuleDescription"],
        sg_flagged,
    )

    write_csv(
        OUTPUT_KEYPAIRS_CSV,
        ["KeyPairName", "KeyPairId", "CreatedDate", "UsedByInstances", "Status"],
        kp_rows,
    )

    # ── Final Summary ─────────────────────────────────────────────────────────
    print_summary(roles_flagged, mfa_rows, sg_flagged, kp_rows)


if __name__ == "__main__":
    main()