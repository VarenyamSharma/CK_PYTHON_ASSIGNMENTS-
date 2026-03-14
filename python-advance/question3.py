import boto3

def region_has_resources(region):

    try:
        # EC2
        ec2 = boto3.client('ec2', region_name=region)
        if ec2.describe_instances()['Reservations']:
            return True

        # RDS
        rds = boto3.client('rds', region_name=region)
        if rds.describe_db_instances()['DBInstances']:
            return True

        # Lambda
        lambda_client = boto3.client('lambda', region_name=region)
        if lambda_client.list_functions()['Functions']:
            return True

        # ECS
        ecs = boto3.client('ecs', region_name=region)
        if ecs.list_clusters()['clusterArns']:
            return True

        # DynamoDB
        dynamodb = boto3.client('dynamodb', region_name=region)
        if dynamodb.list_tables()['TableNames']:
            return True

    except Exception:
        pass

    return False


def get_regions_with_resources():

    ec2 = boto3.client('ec2')
    regions = [r['RegionName'] for r in ec2.describe_regions()['Regions']]

    used_regions = []

    for region in regions:
        print(f"Checking {region}...")

        if region_has_resources(region):
            used_regions.append(region)

    return used_regions


regions = get_regions_with_resources()

print("\nRegions with resources:")
for r in regions:
    print(r)