# 🐍 Python Basics Assignment

> **Assignment submissions for the Python Basics module.**  
> Each question is solved with well-structured Python scripts covering regex, automation, file handling, and more.

---

## 📁 Repository Structure

```
python-basics/
├── q1_ip_email_validator/
│   ├── ques1.py
├── q2_password_generator/
│   ├── with_regex.py
│   └── without_regex.py
├── q3_uptime_monitor/
│   └── uptime_monitor.py
├── q4_package_updater/
│   └── package_updater.py
├── q5_duplicate_finder/
│   └── duplicate_finder.py
├── q6_csv_visualizer/
│   └── csv_visualizer.py
├── q7_ec2_recommendation/
│   └── ec2_recommendation.py
├── q8_json_formatter/
│   ├── json_formatter.py
│   └── sales.json
├── q9_version_control/        # Optional
│   └── version_control.py
└── q10_tuple_update/
    └── tuple_update.py
```

---

## 📋 Questions & Solutions

### Q1 — IP Address & Email Validator

**Problem:** Validate a public IPv4 address and a Gmail address (with informative error messages).  
Solved **with Regex** and **without Regex**.

| Approach | File |
|----------|------|
| With Regex | [with_regex.py](./q1_ip_email_validator/with_regex.py) |
| Without Regex | [without_regex.py](./q1_ip_email_validator/without_regex.py) |

---

### Q2 — Password Generator

**Problem:** Generate a 16-character password with at least one uppercase, one lowercase, two numbers, one special character, no repeating characters, and a random order every time.  
Solved **with Regex** and **without Regex**.

| Approach | File |
|----------|------|
| With Regex | [with_regex.py](./q2_password_generator/with_regex.py) |
| Without Regex | [without_regex.py](./q2_password_generator/without_regex.py) |

---

### Q3 — Uptime Monitoring & Alert System

**Problem:** Continuously monitor a list of URLs, detect HTTP 4xx/5xx errors, alert the user, and optionally log results to a file. Includes support for exponential backoff (bonus).

📄 [uptime_monitor.py](./q3_uptime_monitor/uptime_monitor.py)

**Test URLs used:**
- `http://httpstat.us/404` — 4xx Client Error
- `http://httpstat.us/500` — 5xx Server Error
- `https://www.google.com/` — 200 OK

---

### Q4 — Automating Software Package Updates

**Problem:** Automate checking and updating Linux packages via `apt`/`yum`. Allows updating all packages or a specific one by index, logs failures, and optionally schedules via cron.

📄 [package_updater.py](./q4_package_updater/package_updater.py)

---

### Q5 — Duplicate File Finder & Cleaner

**Problem:** Scan a directory recursively, compute SHA-256 checksums for all files, identify duplicates, and optionally delete or move them. Includes a bonus report generator and minimum file size filter.

📄 [duplicate_finder.py](./q5_duplicate_finder/duplicate_finder.py)

---

### Q6 — CSV to Table Visualizer

**Problem:** Read a CSV file and render a formatted table with borders and proper indentation — without using any third-party table library.

📄 [csv_visualizer.py](./q6_csv_visualizer/csv_visualizer.py)

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

📄 [ec2_recommendation.py](./q7_ec2_recommendation/ec2_recommendation.py)

---

### Q8 — File Restructuring & JSON Formatting

**Problem:** Parse a structured JSON order history, compute total values, apply discounts (10% if order > $100), calculate shipping ($5/item), sort by final total, and export to CSV.

| File | Description |
|------|-------------|
| [json_formatter.py](./q8_json_formatter/json_formatter.py) | Main script |
| [sales.json](./q8_json_formatter/sales.json) | Input data |

**CSV Output Columns:**  
`Order ID, Customer Name, Product Name, Product Price, Quantity Purchased, Total Value, Discount, Shipping Cost, Final Total, Shipping Address, Country Code`

---

### Q9 — File Version Control System *(Optional)*

**Problem:** Simulate a basic version control system — track file changes in a directory, save versioned copies with timestamps, restore previous versions, and optionally diff versions or auto-clean old ones.

📄 [version_control.py](./q9_version_control/version_control.py)

---

### Q10 — Tuple Item Update

**Problem:** Modify a tuple item *without* converting it to a list. Demonstrated with a practical real-world example.

📄 [tuple_update.py](./q10_tuple_update/tuple_update.py)

---

## 🚀 How to Run

```bash
# Clone the repository
git clone https://github.com/VarenyamSharma/CK_PYTHON_ASSIGNMENTS-.git
cd CK_PYTHON_ASSIGNMENTS-/python-basics

# Run any script directly
python q1_ip_email_validator/with_regex.py
python q3_uptime_monitor/uptime_monitor.py
```

**Requirements:** Python 3.8+  
Install dependencies (if any):
```bash
pip install requests
```

---

## 👤 Author

**Varenyam Sharma**  
[GitHub Profile](https://github.com/VarenyamSharma)

---

> 📌 *Note: All file links point to their respective scripts within this repository. Make sure to update the paths if your folder structure differs.*
