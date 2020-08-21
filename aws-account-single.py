import boto3

S3_BUCKET_NAME=""
AWS_ACCESS_KEY_ID=""
AWS_SECRET_ACCESS_KEY=""

print ("== AWS ACCOUNT SETUP ==")

service_calls_to_test = {
    'ec2': 'describe_instances',
    'rds': 'describe_db_instances',
    'elasticache': 'describe_cache_clusters',
    'redshift' : 'describe_clusters',
    'es' : 'list_domain_names'
}

try:
    s3_client = boto3.client('s3',
                             aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    print ("[ PASSED ] S3 Bucket Client Successfully Created")

    s3_setup_passed = False

    for key in s3_client.list_objects(Bucket=S3_BUCKET_NAME)['Contents']:
        if key['Key'] == "aws-programmatic-access-test-object":
            print ("[ PASSED ] S3 Bucket Setup")
            s3_setup_passed = True

    if not s3_setup_passed:
        print ("[ FAILED ] S3 Bucket Setup")
except:
    print("hello")

for service in service_calls_to_test.keys():
    client = boto3.client(service,
                            region_name='us-east-1',
                            aws_access_key_id=AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    try:
        response = getattr(client, service_calls_to_test[service])()
        print ("[ PASSED ] Client Setup for service " + service)
    except:
        print ("[ FAILED ] Client Setup for service " + service)
