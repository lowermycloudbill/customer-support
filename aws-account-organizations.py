import argparse
import sys

is_python3 = sys.version_info[0] >= 3

try:
    import boto3
except ModuleNotFoundError:
    print(' [ INFO ] Boto3 module required. Please install boto3 in your system: `{} install boto3`.'.format('pip3' if is_python3 else 'pip'))
    exit(1)

parser = argparse.ArgumentParser(prog='single-aws-account-tester.py')
parser.add_argument('--access-key', 'accessKey', help='Your AWS access key id')
parser.add_argument('--secret-key', 'secretKey', help='Your AWS access secret key')
parser.add_argument('--bucket-name', 'bucketName', help='Your AWS S3 Bucket name')
parser.add_argument('--role-name', 'roleName', help='Your AWS S3 Bucket name')
args = parser.parse_args()

S3_BUCKET_NAME=args.bucketName
AWS_ACCESS_KEY_ID=args.accessKey
AWS_SECRET_ACCESS_KEY=args.secretKey
ROLE_NAME=args.roleName

print ("== AWS CREDENTIALS ARE ==")

print (" [ INFO ] AWS ACCESS KEY ID IS " + AWS_ACCESS_KEY_ID)
print (" [ INFO ] AWS SECRET ACCESS KEY IS " + AWS_SECRET_ACCESS_KEY)
print (" [ INFO ] S3 BUCKET NAME IS " + S3_BUCKET_NAME)
print (" [ INFO ] ROLE NAME IS " + ROLE_NAME)
  
role_assumption_arn = 'arn:aws:iam::%s:role/'+ROLE_NAME

service_calls_to_test = {
    'ec2': 'describe_instances',
    'rds': 'describe_db_instances',
    'elasticache': 'describe_cache_clusters',
    'redshift' : 'describe_clusters',
    'es' : 'list_domain_names'
}

print ("== ROOT ACCOUNT SETUP ==")

s3_client = boto3.client('s3',
                         aws_access_key_id=AWS_ACCESS_KEY_ID,
                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

s3_setup_passed = False

for key in s3_client.list_objects(Bucket=S3_BUCKET_NAME)['Contents']:
    if key['Key'] == "aws-programmatic-access-test-object":
        print ("[ PASSED ] S3 Bucket Setup")
        s3_setup_passed = True

if not s3_setup_passed:
    print ("[ FAILED ] S3 Bucket Setup")

organizations_client = boto3.client(
    'organizations',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

#Check to make sure List Organizations works
try:
    organisations = organizations_client.list_accounts()
    print ("[ PASSED ] Organization List Accounts")
except:
    print ("[ FAILED ] Organization List Accounts")

sts_client = boto3.client('sts',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

print ("== SUB ACCOUNT SETUP ==")

for organisation in organisations['Accounts']:
    try:
        role_arn = role_assumption_arn % organisation['Id']
        sts_session = sts_client.assume_role(RoleArn=role_arn, RoleSessionName="CloudAdminRoleAssumption")
        print ("[ PASSED ] STS Assume for account " + role_arn)

        aws_access_key = sts_session["Credentials"]["AccessKeyId"]
        aws_access_secret_key = sts_session["Credentials"]["SecretAccessKey"]
        session_token = sts_session["Credentials"]["SessionToken"]

        for service in service_calls_to_test.keys():
            client = boto3.client(  service,
                                    region_name='us-east-1',
                                    aws_access_key_id=aws_access_key,
                                    aws_secret_access_key=aws_access_secret_key,
                                    aws_session_token=session_token
)
            try:
                response = getattr(client, service_calls_to_test[service])()
                print ("[ PASSED ] STS Assume for service " + service + " in account " + role_arn)
            except:
                print ("[ FAILED ] STS Assume for service " + service + " in account " + role_arn)
    except:
        print ("[ FAILED ] STS Assume for account " + role_arn)
