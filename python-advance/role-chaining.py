import boto3

ACCOUNT_B_ROLE = "arn:aws:iam::<ACCOUNT_B_ID>:role/RoleB"
ACCOUNT_C_ROLE = "arn:aws:iam::<ACCOUNT_C_ID>:role/RoleC"

sts = boto3.client("sts")

# Step 1 — Assume Role in Account B
assume_b = sts.assume_role(
    RoleArn=ACCOUNT_B_ROLE,
    RoleSessionName="SessionB"
)

creds_b = assume_b["Credentials"]

sts_b = boto3.client(
    "sts",
    aws_access_key_id=creds_b["AccessKeyId"],
    aws_secret_access_key=creds_b["SecretAccessKey"],
    aws_session_token=creds_b["SessionToken"]
)

# Step 2 — Assume Role in Account C
assume_c = sts_b.assume_role(
    RoleArn=ACCOUNT_C_ROLE,
    RoleSessionName="SessionC"
)

creds_c = assume_c["Credentials"]

# Create EC2 client in Account C
ec2 = boto3.client(
    "ec2",
    aws_access_key_id=creds_c["AccessKeyId"],
    aws_secret_access_key=creds_c["SecretAccessKey"],
    aws_session_token=creds_c["SessionToken"]
)

# Fetch resources from Account C
instances = ec2.describe_instances()

print("\nEC2 Instances in Account C:\n")

for r in instances["Reservations"]:
    for i in r["Instances"]:
        print(i["InstanceId"], i["State"]["Name"])