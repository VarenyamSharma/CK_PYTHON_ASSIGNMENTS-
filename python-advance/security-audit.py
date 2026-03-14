import boto3
import csv

iam = boto3.client('iam')
ec2 = boto3.client('ec2')

# -----------------------------------
# 1. Check IAM Roles with Admin Access
# -----------------------------------
def check_iam_roles():

    rows = []

    roles = iam.list_roles()['Roles']

    for role in roles:

        role_name = role['RoleName']

        attached = iam.list_attached_role_policies(RoleName=role_name)

        for policy in attached['AttachedPolicies']:

            policy_name = policy['PolicyName']

            if "AdministratorAccess" in policy_name:
                rows.append([role_name, policy_name])

    with open("iam_roles_admin_access.csv","w",newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["IAMRoleName","PolicyName"])
        writer.writerows(rows)

    print("IAM role check complete")


# -----------------------------------
# 2. Check MFA for IAM Users
# -----------------------------------
def check_mfa():

    rows = []

    users = iam.list_users()['Users']

    for user in users:

        username = user['UserName']

        mfa = iam.list_mfa_devices(UserName=username)

        enabled = len(mfa['MFADevices']) > 0

        rows.append([username, enabled])

    with open("iam_users_mfa_status.csv","w",newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["IAMUserName","MFAEnabled"])
        writer.writerows(rows)

    print("MFA check complete")


# -----------------------------------
# 3. Security Group Public Access
# -----------------------------------
def check_security_groups():

    rows = []

    groups = ec2.describe_security_groups()['SecurityGroups']

    for sg in groups:

        sg_name = sg['GroupName']

        for perm in sg['IpPermissions']:

            port = perm.get('FromPort')

            if port in [22,80,443]:

                for ip in perm.get('IpRanges',[]):

                    if ip['CidrIp'] == "0.0.0.0/0":

                        rows.append([sg_name, port, "0.0.0.0/0"])

    with open("security_group_public_access.csv","w",newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["SGName","Port","AllowedIP"])
        writer.writerows(rows)

    print("Security group check complete")


# -----------------------------------
# 4. Unused EC2 Key Pairs
# -----------------------------------
def check_unused_keypairs():

    rows = []

    keypairs = ec2.describe_key_pairs()['KeyPairs']
    instances = ec2.describe_instances()

    used_keys = set()

    for r in instances['Reservations']:
        for inst in r['Instances']:

            if 'KeyName' in inst:
                used_keys.add(inst['KeyName'])

    for key in keypairs:

        name = key['KeyName']

        if name not in used_keys:
            rows.append([name])

    with open("unused_keypairs.csv","w",newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["UnusedKeyPairName"])
        writer.writerows(rows)

    print("Keypair check complete")


# -----------------------------------
# Main
# -----------------------------------
if __name__ == "__main__":

    check_iam_roles()
    check_mfa()
    check_security_groups()
    check_unused_keypairs()

    print("\nSecurity audit completed. CSV reports generated.")