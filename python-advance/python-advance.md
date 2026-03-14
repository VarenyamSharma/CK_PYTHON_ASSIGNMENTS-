# ☁️ Python Advanced Assignment — AWS & Boto3

> **Assignment submissions for the Python Advanced module.**  
> All scripts use **Boto3** to interact with AWS services including EC2, IAM, RDS, Lambda, S3, CloudWatch, and Cost Explorer.

---

## 📁 Repository Structure

```
python-advance/
├── q1_ec2_instance_types/
│   └── ec2_instance_types.py
├── q2_transitive_switching/
│   └── transitive_switching.py
├── q3_billed_regions/
│   └── billed_regions.py
├── q4_aws_security/
│   └── aws_security_checks.py
└── q5_cost_optimization/
    └── cost_optimization.py
```

---

## ⚙️ Prerequisites

```bash
# Install dependency
pip install boto3

# Configure AWS credentials
aws configure
```

You will be prompted for:
```
AWS Access Key ID     : <your-access-key>
AWS Secret Access Key : <your-secret-key>
Default region name   : us-east-1
Default output format : json
```

> 💡 For cross-account scripts (Q2), make sure the appropriate IAM roles and trust policies are set up beforehand — see Q2 for the full setup guide.

---

## 📋 Questions & Solutions

---

### Q1 — List All EC2 Instance Types per Region

**Problem:** Fetch all available EC2 instance types across every AWS region using Boto3 — ensuring no duplicates within a region — and export the results to a CSV file.

📄 [ec2_instance_types.py](./q1_ec2_instance_types/ec2_instance_types.py)

**How it works:**
- Iterates over all enabled AWS regions via `describe_regions()`
- Calls `describe_instance_types()` with pagination for each region
- Deduplicates instance types per region using a set
- Writes results to `ec2_instance_types.csv`

**CSV Output:**
```
region,instance_type
us-east-1,t2.micro
us-east-1,t3.medium
eu-west-1,m5.large
...
```

**Run:**
```bash
python q1_ec2_instance_types/ec2_instance_types.py
```

---

### Q2 — Transitive Account Switching (A → B → C)

**Problem:** Access resources in AWS Account C by chaining role assumptions through Account B, starting from Account A. Fetch a resource list from Account C at the end.

📄 [transitive_switching.py](./q2_transitive_switching/transitive_switching.py)

**Role Chain:**
```
Account A  ──assume──▶  Role in Account B  ──assume──▶  Role in Account C  ──▶  Resources
```

#### 🔧 Step-by-Step Setup

**Step 1 — In Account C: Create a role that trusts Account B**
1. Go to IAM → Roles → Create Role
2. Select **Another AWS account** → enter Account B's ID
3. Attach the required permissions (e.g., `AmazonEC2ReadOnlyAccess`)
4. Name it: `RoleInC`
5. Note the ARN: `arn:aws:iam::<ACCOUNT_C_ID>:role/RoleInC`

**Step 2 — In Account B: Create a role that trusts Account A**
1. Go to IAM → Roles → Create Role
2. Select **Another AWS account** → enter Account A's ID
3. Attach an inline policy allowing it to assume `RoleInC`:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "arn:aws:iam::<ACCOUNT_C_ID>:role/RoleInC"
    }
  ]
}
```
4. Name it: `RoleInB`
5. Note the ARN: `arn:aws:iam::<ACCOUNT_B_ID>:role/RoleInB`

**Step 3 — In Account A: Allow your IAM user/role to assume `RoleInB`**

Attach this inline policy to your Account A user or role:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "arn:aws:iam::<ACCOUNT_B_ID>:role/RoleInB"
    }
  ]
}
```

**Step 4 — Run the script**
```bash
python q2_transitive_switching/transitive_switching.py \
  --role-b arn:aws:iam::<ACCOUNT_B_ID>:role/RoleInB \
  --role-c arn:aws:iam::<ACCOUNT_C_ID>:role/RoleInC \
  --region us-east-1
```

The script will assume `RoleInB` first, use those credentials to assume `RoleInC`, then list EC2 instances in Account C.

---

### Q3 — Fetch All Billed / Active Regions

**Problem:** Identify every AWS region where the customer has been billed or currently has active resources, using Cost Explorer and regional service APIs.

📄 [billed_regions.py](./q3_billed_regions/billed_regions.py)

**How it works:**
- Queries AWS **Cost Explorer** (`get_cost_and_usage`) for the past 12 months grouped by region
- Cross-checks with active EC2, RDS, and Lambda resources per region
- Outputs a deduplicated list of regions with any billing activity or live resources

**Sample Output:**
```
Regions with billing or active resources:
  ✅  us-east-1       (billed + active resources)
  ✅  eu-west-1       (billed)
  ✅  ap-southeast-1  (active resources)
```

**Run:**
```bash
python q3_billed_regions/billed_regions.py
```

> ⚠️ Cost Explorer must be enabled in the AWS account. It may incur a small cost (~$0.01 per API request).

---

### Q4 — AWS Security Best Practices Audit

**Problem:** Audit the AWS environment across four security dimensions and produce a CSV report for each, highlighting critical issues that need action.

📄 [aws_security_checks.py](./q4_aws_security/aws_security_checks.py)

#### Checks & Output Files

| # | Check | Output CSV | Columns |
|---|-------|-----------|---------|
| 1 | IAM roles with overly permissive policies | `iam_overpermissive.csv` | `IAMRoleName, PolicyName` |
| 2 | MFA status for all IAM users | `mfa_status.csv` | `IAMUserName, MFAEnabled` |
| 3 | Security groups with public access on ports 22 / 80 / 443 | `sg_public_access.csv` | `SGName, Port, AllowedIP` |
| 4 | EC2 key pairs not attached to any instance | `unused_keypairs.csv` | `KeyPairName, KeyPairId` |

#### Check Details

**Check 1 — Overly Permissive IAM Roles**
- Lists all IAM roles and inspects attached + inline policies
- Flags any role with `AdministratorAccess` or policies containing `"Action": "*"` / `"Resource": "*"`

```
# iam_overpermissive.csv
IAMRoleName,PolicyName
DevOpsRole,AdministratorAccess
LambdaExecutionRole,FullAccessCustomPolicy
```

**Check 2 — MFA Status for IAM Users**
- Lists every IAM user and checks whether a virtual or hardware MFA device is registered
- Reports `True`/`False` for each user

```
# mfa_status.csv
IAMUserName,MFAEnabled
alice,True
bob,False
charlie,False
```

**Check 3 — Security Groups with Public Exposure**
- Scans all security group inbound rules
- Flags rules where source is `0.0.0.0/0` or `::/0` on ports 22 (SSH), 80 (HTTP), 443 (HTTPS)

```
# sg_public_access.csv
SGName,Port,AllowedIP
launch-wizard-1,22,0.0.0.0/0
web-server-sg,80,0.0.0.0/0
```

**Check 4 — Unused EC2 Key Pairs**
- Retrieves all key pairs in the account
- Cross-references with running/stopped EC2 instances
- Reports key pairs with zero associated instances

```
# unused_keypairs.csv
KeyPairName,KeyPairId
old-dev-key,key-0abc123def456
test-keypair,key-0xyz789
```

**Run:**
```bash
python q4_aws_security/aws_security_checks.py
```

---

### Q5 — AWS Cost Optimization Audit

**Problem:** Identify unused or underutilized resources across EC2, RDS, Lambda, and S3 to surface candidates for cost-saving actions.

📄 [cost_optimization.py](./q5_cost_optimization/cost_optimization.py)

#### Resources Checked

| Service | Metric | Threshold | Action Suggested |
|---------|--------|-----------|-----------------|
| **EC2** | Average CPU utilization (30 days) | < 10% | Stop or downsize instance |
| **RDS** | DatabaseConnections (7 days) | = 0 | Stop or delete DB |
| **Lambda** | Invocation count (30 days) | = 0 | Delete unused function |
| **S3** | Object count + last access | 0 objects | Delete bucket |

**How it works:**
- Uses **CloudWatch** `get_metric_statistics` for EC2 CPU and Lambda invocations
- Uses **CloudWatch** for RDS `DatabaseConnections` metric
- Uses **S3** `list_objects_v2` to count objects per bucket
- Prints a consolidated summary report to the console

**Sample Report:**
```
╔══════════════════════════════════════════════════════╗
║         AWS Cost Optimization Report                 ║
╚══════════════════════════════════════════════════════╝

[EC2] Underutilized Instances (Avg CPU < 10% over 30 days):
  ⚠️  i-0abc1234def56789  (t3.medium)   Avg CPU: 2.3%
      → Recommended action: Stop or downsize

[RDS] Idle Instances (0 connections for 7+ days):
  ⚠️  mydb-prod  (db.t3.micro)
      → Recommended action: Stop or delete

[Lambda] Uninvoked Functions (no calls in 30 days):
  ⚠️  process-logs        Last invoked: 2025-01-10
  ⚠️  legacy-data-export  Last invoked: Never
      → Recommended action: Review and delete

[S3] Empty / Unused Buckets:
  ⚠️  dev-temp-uploads    Objects: 0
  ⚠️  old-backup-2023     Objects: 0
      → Recommended action: Delete bucket

══════════════════════════════════════════════════════
  Total candidates found: 6 resource(s)
══════════════════════════════════════════════════════
```

**Run:**
```bash
python q5_cost_optimization/cost_optimization.py
```

---

## 🚀 How to Run All Scripts

```bash
# Clone the repo
git clone https://github.com/VarenyamSharma/CK_PYTHON_ASSIGNMENTS-.git
cd CK_PYTHON_ASSIGNMENTS-/python-advance

# Install dependency
pip install boto3

# Configure AWS
aws configure

# Run individual scripts
python q1_ec2_instance_types/ec2_instance_types.py
python q2_transitive_switching/transitive_switching.py
python q3_billed_regions/billed_regions.py
python q4_aws_security/aws_security_checks.py
python q5_cost_optimization/cost_optimization.py
```

---

## 🔐 IAM Permissions Required

| Script | Minimum IAM Permissions Needed |
|--------|-------------------------------|
| Q1 — EC2 Instance Types | `ec2:DescribeRegions`, `ec2:DescribeInstanceTypes` |
| Q2 — Transitive Switching | `sts:AssumeRole` (on Account A and B roles) |
| Q3 — Billed Regions | `ce:GetCostAndUsage`, `ec2:DescribeInstances`, `rds:DescribeDBInstances`, `lambda:ListFunctions` |
| Q4 — Security Audit | `iam:ListRoles`, `iam:ListAttachedRolePolicies`, `iam:ListUsers`, `iam:ListMFADevices`, `ec2:DescribeSecurityGroups`, `ec2:DescribeKeyPairs`, `ec2:DescribeInstances` |
| Q5 — Cost Optimization | `ec2:DescribeInstances`, `rds:DescribeDBInstances`, `lambda:ListFunctions`, `s3:ListBuckets`, `s3:ListObjectsV2`, `cloudwatch:GetMetricStatistics` |

---

## 👤 Author

**Varenyam Sharma**  
[GitHub Profile](https://github.com/VarenyamSharma)

---

> 📌 *All file links are relative to the `python-advance/` directory. Update paths if your folder structure differs.*  
> ⚠️ *Never hardcode AWS credentials in scripts. Always use `aws configure`, environment variables, or IAM instance roles.*
