# customer-support

Simple scripts to test out CloudAdmin integration.

## Required libs
- boto3
- azure-mgmt-reservations
- azure-storage-blob (v2.0.1)

## Usage

```shell
python3 aws-account-organizations.py --access-key <aws-access-key-id> --secret-key <aws-access-secret-id> --bucket-name <s3-bucket-name> --role-arn <role-arn>

python3 aws-account-single.py --access-key <aws-access-key-id> --secret-key <aws-access-secret-id> --bucket-name <s3-bucket-name>

python3 azure-account.py --client-id <client-id> --client-secret <client-secret> --subscription-id <subscription-id> --tenant-id <tenant-id>

python3 aws-s3.py --access-key <aws-access-key-id> --secret-key <aws-access-secret-id> --bucket-name <s3-bucket-name> --bucket-prefix <s3-bucket-prefix> --role-arn <s3-role-arn>

python3 azure-storage.py --bucket-key <bucket-key> --bucket-name <bucket-name>
```

