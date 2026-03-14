import boto3
from datetime import datetime, timedelta

# Clients
ec2 = boto3.client("ec2")
cloudwatch = boto3.client("cloudwatch")
rds = boto3.client("rds")
lambda_client = boto3.client("lambda")
s3 = boto3.client("s3")

LOW_CPU_THRESHOLD = 10
DAYS_30 = 30
DAYS_7 = 7

now = datetime.utcnow()
start_30 = now - timedelta(days=DAYS_30)
start_7 = now - timedelta(days=DAYS_7)

# -----------------------------
# 1. EC2 Low CPU Utilization
# -----------------------------
def check_ec2():
    print("\nChecking EC2 Instances...")
    low_cpu_instances = []

    instances = ec2.describe_instances()

    for reservation in instances["Reservations"]:
        for instance in reservation["Instances"]:

            instance_id = instance["InstanceId"]
            state = instance["State"]["Name"]

            if state != "running":
                continue

            metrics = cloudwatch.get_metric_statistics(
                Namespace="AWS/EC2",
                MetricName="CPUUtilization",
                Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                StartTime=start_30,
                EndTime=now,
                Period=86400,
                Statistics=["Average"],
            )

            datapoints = metrics["Datapoints"]

            if datapoints:
                avg_cpu = sum(d["Average"] for d in datapoints) / len(datapoints)

                if avg_cpu < LOW_CPU_THRESHOLD:
                    low_cpu_instances.append((instance_id, avg_cpu))

    return low_cpu_instances


# -----------------------------
# 2. Idle RDS Instances
# -----------------------------
def check_rds():
    print("\nChecking RDS Instances...")
    idle_rds = []

    instances = rds.describe_db_instances()

    for db in instances["DBInstances"]:
        db_id = db["DBInstanceIdentifier"]
        status = db["DBInstanceStatus"]

        if status != "available":
            continue

        metrics = cloudwatch.get_metric_statistics(
            Namespace="AWS/RDS",
            MetricName="DatabaseConnections",
            Dimensions=[{"Name": "DBInstanceIdentifier", "Value": db_id}],
            StartTime=start_7,
            EndTime=now,
            Period=86400,
            Statistics=["Average"],
        )

        datapoints = metrics["Datapoints"]

        if datapoints:
            avg_conn = sum(d["Average"] for d in datapoints) / len(datapoints)

            if avg_conn == 0:
                idle_rds.append(db_id)

    return idle_rds


# -----------------------------
# 3. Unused Lambda Functions
# -----------------------------
def check_lambda():
    print("\nChecking Lambda Functions...")
    unused_lambda = []

    functions = lambda_client.list_functions()["Functions"]

    for func in functions:
        name = func["FunctionName"]

        metrics = cloudwatch.get_metric_statistics(
            Namespace="AWS/Lambda",
            MetricName="Invocations",
            Dimensions=[{"Name": "FunctionName", "Value": name}],
            StartTime=start_30,
            EndTime=now,
            Period=86400,
            Statistics=["Sum"],
        )

        datapoints = metrics["Datapoints"]

        total_invocations = sum(d["Sum"] for d in datapoints)

        if total_invocations == 0:
            unused_lambda.append(name)

    return unused_lambda


# -----------------------------
# 4. Unused S3 Buckets
# -----------------------------
def check_s3():
    print("\nChecking S3 Buckets...")
    empty_buckets = []

    buckets = s3.list_buckets()["Buckets"]

    for bucket in buckets:
        name = bucket["Name"]

        try:
            objects = s3.list_objects_v2(Bucket=name, MaxKeys=1)

            if "Contents" not in objects:
                empty_buckets.append(name)

        except Exception:
            pass

    return empty_buckets


# -----------------------------
# MAIN REPORT
# -----------------------------
if __name__ == "__main__":

    ec2_results = check_ec2()
    rds_results = check_rds()
    lambda_results = check_lambda()
    s3_results = check_s3()

    print("\n==============================")
    print("AWS COST OPTIMIZATION REPORT")
    print("==============================")

    print("\nEC2 Instances with Low CPU (<10%)")
    for inst in ec2_results:
        print(f"Instance: {inst[0]} | Avg CPU: {inst[1]:.2f}%")

    print("\nIdle RDS Instances (No connections in 7 days)")
    for db in rds_results:
        print(f"RDS Instance: {db}")

    print("\nUnused Lambda Functions (No invocations in 30 days)")
    for func in lambda_results:
        print(f"Lambda Function: {func}")

    print("\nEmpty / Unused S3 Buckets")
    for bucket in s3_results:
        print(f"S3 Bucket: {bucket}")

    print("\nSuggested Actions:")
    print("• Stop or terminate low-utilization EC2 instances")
    print("• Stop or delete unused RDS instances")
    print("• Delete unused Lambda functions")
    print("• Remove empty S3 buckets")