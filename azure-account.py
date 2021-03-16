import argparse
import sys

from azure.mgmt.reservations.models import ErrorException
from msrestazure.azure_exceptions import CloudError

is_python3 = sys.version_info[0] >= 3

try:
    import azure.mgmt.reservations
except ModuleNotFoundError:
    print(' [ INFO ] azure-mgmt-reservations module required. Please install: `{} install azure-mgmt-reservations`.'.format('pip3' if is_python3 else 'pip'))
    exit(1)


from msrest.exceptions import AuthenticationError
from msrestazure.azure_active_directory import ServicePrincipalCredentials
from azure.mgmt.reservations import AzureReservationAPI

parser = argparse.ArgumentParser(prog='azure-account.py')
parser.add_argument('--client-id', type=str, dest='clientKey', help='Your Azure client id')
parser.add_argument('--tenant-id', type=str, dest='tenantKey', help='Your Azure tenant id')
parser.add_argument('--subscription-id', type=str, dest='subscriptionKey', help='Your Azure subscription id')
parser.add_argument('--client-secret', type=str, dest='secretKey', help='Your Azure client secret')
args = parser.parse_args()

client_id = args.clientKey
client_secret = args.secretKey
subscription_id = args.subscriptionKey
tenant_id = args.tenantKey

if not client_id or not client_secret or not tenant_id or not subscription_id:
    parser.print_help()
    print(' [ INFO ] Azure Client Id, Client Secret, Subscription Id, and Tenant Id are required.')
    exit(1)

print("\n== AZURE CREDENTIALS ==")

print(" [ INFO ] AZURE CLIENT ID IS: '{}'".format(client_id))
print(" [ INFO ] AZURE CLIENT SECRET IS: '{}'".format(client_secret))
print(" [ INFO ] AZURE TENANT ID IS: '{}'".format(tenant_id))
print(" [ INFO ] AZURE SUBSCRIPTION ID IS: '{}'".format(subscription_id))

print("\n== RUNNING AZURE TESTS ==")


def check_credentials():
    global service_credentials
    try:
        print("[ INFO ] Checking Service Credentials")
        service_credentials = ServicePrincipalCredentials(
            client_id=client_id,
            secret=client_secret,
            tenant=tenant_id
        )
        print("[ PASSED ] Checking Service Credentials")
    except AuthenticationError as ex:
        print("Error description:")
        print(str(ex))
        print("[ FAILED ] Checking Service Credentials\n")
        exit(1)


def check_permissions():
    try:
        print("[ INFO ] Checking Reservations Permissions")
        calculate_body = {
            'sku': {
                'name': 'Standard_B1ls'
            },
            'location': 'eastus',
            'properties': {
                'reservedResourceType': 'virtualMachines',
                'billingScopeId': '/subscriptions/' + subscription_id,
                'term': 'P1Y',
                'quantity': 1,
                'displayName': 'TestPolling',
                'billingPlan': 'Upfront',
                'appliedScopes': ['/subscriptions/' + subscription_id],
                'appliedScopeType': 'Single',
                'reservedResourceProperties': {
                    'instanceFlexibility': 'On'
                }
            },
        }
        reservations_client = AzureReservationAPI(service_credentials)
        calculate_response = reservations_client.reservation_order.calculate(body=calculate_body)
        print("[ PASSED ] Checking Reservations Permissions\n")
    except (CloudError, ErrorException) as ex:
        print("Error description:")
        print(str(ex))
        print("[ FAILED ] Checking Reservations Permissions\n")
        exit(1)


check_credentials()
check_permissions()
