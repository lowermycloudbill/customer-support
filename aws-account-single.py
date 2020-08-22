import boto3
import argparse

parser = argparse.ArgumentParser(prog='single-aws-account-tester.py')
parser.add_argument('accessKey', help='Your AWS access key id')
parser.add_argument('secretKey', help='Your AWS access secret key')
parser.add_argument('bucketName', help='Your AWS S3 Bucket name')
args = parser.parse_args()


S3_BUCKET_NAME=args.bucketName
AWS_ACCESS_KEY_ID=args.accessKey
AWS_SECRET_ACCESS_KEY=args.secretKey

print ("== AWS CREDENTIALS ARE ==")

print (" [ INFO ] AWS ACCESS KEY ID IS " + AWS_ACCESS_KEY_ID)
print (" [ INFO ] AWS SECRET ACCESS KEY IS " + AWS_SECRET_ACCESS_KEY)
print (" [ INFO ] S3 BUCKET NAME IS " + S3_BUCKET_NAME)

print ("== RUNNING AWS TESTS ==")

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
            print ("[ PASSED ] S3 Bucket List")
            s3_setup_passed = True

    if not s3_setup_passed:
        print ("[ FAILED ] S3 Bucket List")
except:
    print ("[ FAILED ] S3 Bucket List")

for service in service_calls_to_test.keys():
    client = boto3.client(  service,
                            region_name='us-east-1',
                            aws_access_key_id=AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    try:
        response = getattr(client, service_calls_to_test[service])()
        print ("[ PASSED ] Client Setup for service " + service)
    except:
        print ("[ FAILED ] Client Setup for service " + service)
