# 🐍 Python Assignments — Basics & Advanced

> **Assignment submissions covering Python fundamentals, automation, AWS/Boto3, and cloud cost & security best practices.**

---

## 📁 Repository Structure

```
CK_PYTHON_ASSIGNMENTS-/
├── python-basics/
│   ├── q1_ip_email_validator/
│   │   ├── ques1.py
│   ├── q2_password_generator/
│   │   ├── with_regex.py
│   │   └── without_regex.py
│   ├── q3_uptime_monitor/
│   │   └── uptime_monitor.py
│   ├── q4_package_updater/
│   │   └── package_updater.py
│   ├── q5_duplicate_finder/
│   │   └── duplicate_finder.py
│   ├── q6_csv_visualizer/
│   │   └── csv_visualizer.py
│   ├── q7_ec2_recommendation/
│   │   └── ec2_recommendation.py
│   ├── q8_json_formatter/
│   │   ├── json_formatter.py
│   │   └── sales.json
│   ├── q9_version_control/
│   │   └── version_control.py
│   └── q10_tuple_update/
│       └── tuple_update.py
│
└── python-advance/
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

## 📘 Python Basics

### Q1 — IP Address & Email Validator

**Problem:** Validate a public IPv4 address and a Gmail address (with informative error messages).  
Solved **with Regex** and **without Regex**.

| Approach | File |
|----------|------|
| With Regex | [with_regex.py](./python-basics/q1_ip_email_validator/with_regex.py) |
| Without Regex | [without_regex.py](./python-basics/q1_ip_email_validator/without_regex.py) |

---

### Q2 — Password Generator

**Problem:** Generate a 16-character password with at least one uppercase, one lowercase, two numbers, one special character, no repeating characters, and a random order every time.  
Solved **with Regex** and **without Regex**.

| Approach | File |
|----------|------|
| With Regex | [with_regex.py](./python-basics/q2_password_generator/with_regex.py) |
| Without Regex | [without_regex.py](./python-basics/q2_password_generator/without_regex.py) |

---

### Q3 — Uptime Monitoring & Alert System

**Problem:** Continuously monitor a list of URLs, detect HTTP 4xx/5xx errors, alert the user, and log results to a file. Includes exponential backoff (bonus).

📄 [uptime_monitor.py](./python-basics/q3_uptime_monitor/uptime_monitor.py)

**Test URLs used:**
- `http://httpstat.us/404` — 4xx Client Error
- `http://httpstat.us/500` — 5xx Server Error
- `https://www.google.com/` — 200 OK

---

### Q4 — Automating Software Package Updates

**Problem:** Automate checking and updating Linux packages via `apt`/`yum`. Allows updating all packages or a specific one by index, logs failures, and optionally schedules via cron.

📄 [package_updater.py](./python-basics/q4_package_updater/package_updater.py)

---

### Q5 — Duplicate File Finder & Cleaner

**Problem:** Scan a directory recursively, compute SHA-256 checksums, identify duplicates, and optionally delete or move them. Includes a bonus report generator and minimum file size filter.

📄 [duplicate_finder.py](./python-basics/q5_duplicate_finder/duplicate_finder.py)

---

### Q6 — CSV to Table Visualizer

**Problem:** Read a CSV file and render a formatted table with borders and proper indentation — without using any third-party table library.

📄 [csv_visualizer.py](./python-basics/q6_csv_visualizer/csv_visualizer.py)

**Example Output:**
```
+---------+-----+-------------+
| Name    | Age | Department  |
+---------+-----+-------------+
| Alice   |  30 | HR          |
| Bob     |  25 | Engineering |
| Charlie |  35 | Marketing   |
| Diana   |  28 | Sales       |
+---------+-----+-------------+
```

---

### Q7 — EC2 Instance Recommendation

**Problem:** Recommend an EC2 instance based on current instance type and CPU utilization.
- CPU < 20% → downgrade by one size
- CPU 20–80% → same size, suggest latest generation
- CPU > 80% → upgrade by one size

Output is rendered as a formatted table (reusing the Q6 function).

📄 [ec2_recommendation.py](./python-basics/q7_ec2_recommendation/ec2_recommendation.py)

---

### Q8 — File Restructuring & JSON Formatting

**Problem:** Parse a structured JSON order history, compute total values, apply discounts (10% if order > $100), calculate shipping ($5/item), sort by final total, and export to CSV.

| File | Description |
|------|-------------|
| [json_formatter.py](./python-basics/q8_json_formatter/json_formatter.py) | Main script |
| [sales.json](./python-basics/q8_json_formatter/sales.json) | Input data |

**CSV Output Columns:**  
`Order ID, Customer Name, Product Name, Product Price, Quantity Purchased, Total Value, Discount, Shipping Cost, Final Total, Shipping Address, Country Code`

---

### Q9 — File Version Control System *(Optional)*

**Problem:** Simulate a basic version control system — track file changes in a directory, save versioned copies with timestamps, restore previous versions, and optionally diff versions or auto-clean old ones.

📄 [version_control.py](./python-basics/q9_version_control/version_control.py)

**Usage:**
```bash
python vcs.py watch  ./myproject                    # start monitoring
python vcs.py list   ./myproject                    # list all versions
python vcs.py restore ./myproject notes.txt 2       # restore to v2
python vcs.py diff   ./myproject notes.txt 1 3      # diff v1 vs v3
python vcs.py cleanup ./myproject --keep 3          # keep last 3 only
```

---

### Q10 — Tuple Item Update

**Problem:** Modify a tuple item *without* converting it to a list. Demonstrated with a practical real-world example.

📄 [tuple_update.py](./python-basics/q10_tuple_update/tuple_update.py)

---

## 📗 Python Advanced (AWS / Boto3)

> **Prerequisites:** AWS credentials configured via `aws configure` or environment variables.  
> Install dependency: `pip install boto3`

---

### Q1 — List All EC2 Instance Types per Region

**Problem:** Use Boto3 to fetch all available EC2 instance types across every AWS region — no duplicates per region — and export to a CSV.

📄 [ec2_instance_types.py](./python-advance/q1_ec2_instance_types/ec2_instance_types.py)

**CSV Output Columns:**
```
region, instance_type
```

---

### Q2 — Transitive Account Switching (A → B → C)

**Problem:** Access AWS Account C through Account B (cross-account role chaining) starting from Account A, then list resources from Account C.

Covers full step-by-step setup:
1. Create IAM role in Account C trusting Account B
2. Create IAM role in Account B trusting Account A with permission to assume the Account C role
3. Python script to assume roles transitively and fetch resources from Account C

📄 [transitive_switching.py](./python-advance/q2_transitive_switching/transitive_switching.py)

**Role Chain:**
```
Account A  ──assume──▶  Account B Role  ──assume──▶  Account C Role  ──▶  Resources
```

---

### Q3 — Fetch All Billed / Active Regions

**Problem:** Identify all AWS regions where a customer has been billed or has any active resources — using Cost Explorer and service APIs.

📄 [billed_regions.py](./python-advance/q3_billed_regions/billed_regions.py)

---

### Q4 — AWS Security Best Practices Audit

**Problem:** Audit the AWS environment across four security dimensions and generate a CSV report for each.

📄 [aws_security_checks.py](./python-advance/q4_aws_security/aws_security_checks.py)

| Check | Output CSV | Columns |
|-------|-----------|---------|
| IAM roles with overly permissive policies | `iam_overpermissive.csv` | `IAMRoleName, PolicyName` |
| IAM users without MFA enabled | `mfa_status.csv` | `IAMUserName, MFAEnabled` |
| Security groups with public access on sensitive ports | `sg_public_access.csv` | `SGName, Port, AllowedIP` |
| Unused EC2 key pairs | `unused_keypairs.csv` | `KeyPairName, KeyPairId` |

**Checks performed:**
- Roles attached with `AdministratorAccess` or `*` wildcard policies
- MFA status (`True`/`False`) for every IAM user
- Inbound rules open to `0.0.0.0/0` on ports 22, 80, 443
- Key pairs not associated with any running EC2 instance

---

### Q5 — AWS Cost Optimization Audit

**Problem:** Identify unused or underutilized resources across EC2, RDS, Lambda, and S3 to recommend cost-saving actions.

📄 [cost_optimization.py](./python-advance/q5_cost_optimization/cost_optimization.py)

| Resource | Condition Checked |
|----------|------------------|
| **EC2** | CPU utilization < 10% over the past 30 days (via CloudWatch) |
| **RDS** | Zero DB connections for over 7 days (via CloudWatch) |
| **Lambda** | No invocations in the last 30 days (via CloudWatch) |
| **S3** | Buckets with zero objects or no recent access |

**Sample Report Output:**
```
===== Cost Optimization Report =====

[EC2] Underutilized Instances (CPU < 10%):
  - i-0abc123  (t3.medium)  Avg CPU: 2.3%  → Consider stopping or downsizing

[RDS] Idle Instances (no connections > 7 days):
  - mydb-instance  (db.t3.micro)  → Consider stopping or deleting

[Lambda] Uninvoked Functions (30 days):
  - process-logs  Last invoked: 2024-11-01  → Consider removing

[S3] Unused Buckets:
  - dev-backup-bucket  Objects: 0  → Consider deleting
```

---

## 🚀 How to Run

```bash
# Clone the repository
git clone https://github.com/VarenyamSharma/CK_PYTHON_ASSIGNMENTS-.git

# ── Basics ──────────────────────────────────────────────
cd CK_PYTHON_ASSIGNMENTS-/python-basics
pip install requests
python q1_ip_email_validator/with_regex.py
python q3_uptime_monitor/uptime_monitor.py
python q9_version_control/version_control.py watch ./mydir

# ── Advanced (AWS) ───────────────────────────────────────
cd ../python-advance
pip install boto3
aws configure                            # set up your credentials first
python q1_ec2_instance_types/ec2_instance_types.py
python q4_aws_security/aws_security_checks.py
python q5_cost_optimization/cost_optimization.py
```

---

## 🛠 Requirements

| Module | Dependency |
|--------|-----------|
| Python Basics | Python 3.8+, `requests` |
| Python Advanced | Python 3.8+, `boto3`, AWS credentials configured |

---

## 👤 Author

**Varenyam Sharma**  
[GitHub Profile](https://github.com/VarenyamSharma)

---

> 📌 *Note: All file links point to their respective scripts within this repository. Make sure to update the paths if your folder structure differs.*
