import boto3

S3_BUCKET_NAME=""
AWS_ACCESS_KEY_ID=""
AWS_SECRET_ACCESS_KEY=""
ROLE_NAME=""

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
        #Perfect let's just go through each necessary vertical and make sure that we can do a describe or list
        #EC2

        aws_access_key = sts_session["Credentials"]["AccessKeyId"]
        aws_access_secret_key = sts_session["Credentials"]["SecretAccessKey"]
        session_token = sts_session["Credentials"]["SessionToken"]

        for service in service_calls_to_test.keys():
            client = boto3.client(  service,
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
