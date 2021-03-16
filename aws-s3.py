import argparse
import sys

is_python3 = sys.version_info[0] >= 3

try:
    import boto3
    from botocore.exceptions import ClientError
except ModuleNotFoundError:
    print(' [ INFO ] Boto3 module required. Please install boto3 in your system: `{} install boto3`.'.format('pip3' if is_python3 else 'pip'))
    exit(1)

parser = argparse.ArgumentParser(prog='aws-s3.py')
parser.add_argument('--access-key', type=str, dest='accessKey', help='Your AWS access key id')
parser.add_argument('--secret-key', type=str, dest='secretKey', help='Your AWS access secret key')
parser.add_argument('--bucket-name', type=str, dest='bucketName', help='Your AWS S3 Bucket name')
parser.add_argument('--bucket-prefix', type=str, dest='bucketPrefix', default=None, help='Your AWS S3 Bucket prefix')
parser.add_argument('--role-arn', type=str, dest='roleArn', default=None, help='Your AWS role arn in case of assuming a role (optional)')
args = parser.parse_args()

s3_bucket_name = args.bucketName
s3_bucket_prefix = args.bucketPrefix
s3_role_arn = args.roleArn
aws_access_key_id = args.accessKey
aws_secret_access_key = args.secretKey

if not s3_bucket_name or not aws_access_key_id or not aws_secret_access_key:
    parser.print_help()
    print(' [ INFO ] AWS Access key, AWS Access Secret key and bucket name are required.')
    exit(1)

print("\n== AWS CREDENTIALS ==")

print(" [ INFO ] AWS ACCESS KEY ID IS: '{}'".format(aws_access_key_id))
print(" [ INFO ] AWS SECRET ACCESS KEY IS: '{}'".format(aws_secret_access_key))
print(" [ INFO ] S3 BUCKET NAME IS: '{}'".format(s3_bucket_name))

if s3_bucket_prefix:
    print(" [ INFO ] S3 BUCKET PREFIX IS: '{}'".format(s3_bucket_prefix))

if s3_role_arn:
    print(" [ INFO ] S3 ROLE NAME IS: '{}'".format(s3_role_arn))

print("\n== RUNNING S3 TESTS ==")


def check_bucket():
    try:
        print("[ INFO ] Checking S3 Bucket")
        s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        kwargs = {
            'Bucket': s3_bucket_name,
            'MaxKeys': 1,
        }
        if s3_bucket_prefix:
            kwargs['Prefix'] = s3_bucket_prefix + '/' if not s3_bucket_prefix.endswith('/') else s3_bucket_prefix
        resp = s3_client.list_objects_v2(**kwargs)
        print("[ PASSED ] Checking S3 Bucket\n")
    except ClientError as ex:
        print("Error description:")
        print(str(ex))
        print("[ FAILED ] Checking S3 Bucket\n")
        exit(1)


def check_organization_bucket(role_arn):
    try:
        print("[ INFO ] Checking access to S3 Bucket for role {}".format(role_arn))

        sts_client = boto3.client('sts', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        response = sts_client.assume_role(RoleArn=role_arn, RoleSessionName='CloudAdmin')
        access, secret, token = (response['Credentials']['AccessKeyId'], response['Credentials']['SecretAccessKey'], response['Credentials']['SessionToken'])

        s3_client = boto3.client('s3', aws_access_key_id=access, aws_secret_access_key=secret, aws_session_token=token)
        kwargs = {
            'Bucket': s3_bucket_name,
            'MaxKeys': 1,
        }
        if s3_bucket_prefix:
            kwargs['Prefix'] = s3_bucket_prefix + '/' if s3_bucket_prefix.endswith('/') else s3_bucket_prefix
        resp = s3_client.list_objects_v2(**kwargs)
        print("[ PASSED ] Checking S3 Bucket\n")
    except ClientError as ex:
        print("Error description:")
        print(str(ex))
        print("[ FAILED ] Checking S3 Bucket\n")
        exit(1)


if s3_role_arn:
    check_organization_bucket(s3_role_arn)
else:
    check_bucket()
