#!/bin/bash
set -e

DATE=$(date -I)
echo "Today's date: $DATE"
echo

echo '== Setup Starting'
echo

### Select a subscription

SUBSCRIPTIONS=$(az account list)

echo 'Available subscriptions: '
echo "$SUBSCRIPTIONS" | jq -r '(["ID","NAME", "IS_DEFAULT"] | (., map(length*"-"))), (.[] | [.id, .name, .isDefault]) | @tsv' | column -ts $'\t'
echo

while true; do
  echo -n 'Enter subscription id: '
  read -r SELECTED_SUBSCRIPTION_ID

  SELECTED_SUBSCRIPTION=$(echo "$SUBSCRIPTIONS" | jq -r --arg id "$SELECTED_SUBSCRIPTION_ID" '.[]|select(.id==$id)')

  if [[ $SELECTED_SUBSCRIPTION ]]; then
    break
  fi
done

echo "Press enter to continue.."
read -r REPLY

### Create app registration and assign roles

echo '== Registering app'
echo '. Creating app registration'

APP_NAME='CloudAdmin.Service.AUTOMATION'

APP_ID=$(az ad app create --display-name "$APP_NAME" --only-show-errors | jq -r '.appId')
APP_SECRET=$(az ad app credential reset --id "$APP_ID" --years 1000 --only-show-errors | jq -r '.password')

APP_SP=$(az ad sp list --query "[?appId=='$APP_ID']" --all | jq -r 'first(.[])')
if [[ $APP_SP == "" ]]; then
  echo '. Creating service principal'
  az ad sp create --id "$APP_ID" -o none
else
  echo ". Using existing service principal"
fi

echo '== Searching app permissions for Azure Management Service'
APP_PERMISSION=$(az ad app permission list-grants --show-resource-name --query "[?resourceDisplayName=='Windows Azure Service Management API'] | [?expiryTime > '$DATE']" | jq '.[0]')
echo "Permission found: $APP_PERMISSION"

PERMISSION_ID=$("$APP_PERMISSION" | jq '.objectId')
echo "Permission id: $PERMISSION_ID"

echo '. Granting Permissions to app'
az ad app permission grant --id "$APP_ID" --api "$PERMISSION_ID" -o none

# assign roles to the apps
echo '== Assigning roles to the app'
sleep 8s # a new service principal is not usable for role assignment instantly, neither after couple of seconds.. :)

echo '. Assigning Reservation Purchaser role to app'
az role assignment create --assignee "$APP_ID" --role 'Reservation Purchaser' -o none

ROLE_NAME="CloudAdminService"

ROLE_DEFINITION="{
   \"Name\": \"$ROLE_NAME\",
   \"Description\": \"Required permissions for CloudAdmin Services\",
   \"IsCustom\": true,
   \"AssignableScopes\": [
       \"/subscriptions/$SELECTED_SUBSCRIPTION_ID\"
   ],
   \"Actions\": [
        \"*/read\",
        \"Microsoft.Compute/virtualMachines/start/action\",
        \"Microsoft.Compute/virtualMachines/restart/action\",
        \"Microsoft.Compute/virtualMachines/powerOff/action\",
        \"Microsoft.Compute/disks/delete\",
        \"Microsoft.Compute/snapshots/delete\",
        \"Microsoft.Sql/servers/databases/resume/action\",
        \"Microsoft.Sql/servers/databases/pause/action\",
        \"Microsoft.Network/loadBalancers/delete\",
        \"Microsoft.Network/publicIPAddresses/delete\"
   ],
   \"NotActions\": []
}"

echo '. Checking if custom role exists'
ROLE_DEFINITION_QUERIED=$(az role definition list --name "$ROLE_NAME")

if [[ "$ROLE_DEFINITION_QUERIED" == "" ]]; then
  echo '. Creating custom role for CloudAdmin'
  az role definition create --role-definition "$ROLE_DEFINITION"
else
  echo '. Updating custom role for CloudAdmin'
  az role definition update --role-definition "$ROLE_DEFINITION"
fi

echo '. Assigning custom role to app'
az role assignment create --assignee "$APP_ID" --role "$ROLE_NAME" -o none

### Print results
echo "--------------------------------------------------------------------------------"
echo "Save and use the following json to onboard credentials into CloudAdmin"
cat << EOF
{
  "subscriptionId": "$SELECTED_SUBSCRIPTION_ID",
  "tenantId": "$(echo "$SELECTED_SUBSCRIPTION" | jq -r '.tenantId')",
  "clientId": "$APP_ID",
  "clientSecret": "$APP_SECRET"
}
EOF
