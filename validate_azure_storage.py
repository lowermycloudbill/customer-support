import argparse
import sys

import requests

is_python3 = sys.version_info[0] >= 3

try:
    import azure.storage.blob
except ModuleNotFoundError:
    print(' [ INFO ] azure-storage-blob module required. Please install: `{} install azure-storage-blob==2.0.1`.'.format('pip3' if is_python3 else 'pip'))
    exit(1)
try:
    from azure.storage.blob import BlockBlobService
except ImportError:
    print(' [ INFO ] azure-storage-blob version 2.0.1 is required. Please install: `{} install azure-storage-blob==2.0.1`.'.format('pip3' if is_python3 else 'pip'))
    exit(1)

parser = argparse.ArgumentParser(prog='validate_azure_storage.py')
parser.add_argument('--bucket-name', type=str, dest='bucketName', help='Your Azure Bucket name')
parser.add_argument('--bucket-key', type=str, dest='bucketKey', help='Your Azure Bucket key string')
args = parser.parse_args()

bucket_name = args.bucketName
bucket_key = args.bucketKey

if not bucket_name or not bucket_key:
    parser.print_help()
    print(' [ INFO ] Azure bucket name and bucket key are required.')
    exit(1)

print("\n== AZURE CREDENTIALS ==")

print(" [ INFO ] STORAGE BUCKET NAME IS: '{}'".format(bucket_name))
print(" [ INFO ] STORAGE BUCKET KEY IS: '{}'".format(bucket_key))

print("\n== RUNNING STORAGE TESTS ==")


def check_bucket():
    try:
        print("[ INFO ] Checking Storage Bucket")
        blob_service = BlockBlobService(bucket_name, bucket_key)
        url = blob_service.protocol + '://' + blob_service.primary_endpoint
        requests.get(url)
        print("[ PASSED ] Checking Storage Bucket")

        print("[ INFO ] Checking billing container on Bucket")
        try:
            blob_service.get_container_properties('billing')
            print("[ PASSED ] Checking billing container on Bucket")
        except Exception as ex:
            print("Error description:")
            print(str(ex))
            print("[ FAILED ] Checking billing container on Bucket\n")
            exit(1)
    except Exception as ex:
        print("Error description:")
        print(str(ex))
        print("[ FAILED ] Checking Storage Bucket\n")
        exit(1)


check_bucket()
