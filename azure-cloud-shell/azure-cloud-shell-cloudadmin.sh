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
  echo -n 'Enter subscription id to use with CloudAdmin: '
  read -r SELECTED_SUBSCRIPTION_ID

  SELECTED_SUBSCRIPTION=$(echo "$SUBSCRIPTIONS" | jq -r --arg id "$SELECTED_SUBSCRIPTION_ID" '.[]|select(.id==$id)')

  if [[ $SELECTED_SUBSCRIPTION ]]; then
    break
  fi
done

echo

### Create app registration and assign roles

APP_NAME='CloudAdmin.Service.AUTOMATION'

echo "== Checking app $APP_NAME"

APP=$(az ad app list --display-name "$APP_NAME")

if [[ "$APP" != '[]' ]]; then
  APP_ID=$(jq -r '.[0].appId' <<< "$APP")
else
  echo '. Creating app registration'
  APP_ID=$(az ad app create --display-name "$APP_NAME" --only-show-errors | jq -r '.appId')
fi

echo ". App registration id: $APP_ID"

APP_SECRET=$(az ad app credential reset --id "$APP_ID" --years 1000 --only-show-errors | jq -r '.password')

echo '== Checking app Service Principal'
APP_SP=$(az ad sp list --query "[?appId=='$APP_ID']" --all | jq 'first(.[])')

if [[ $APP_SP != '' ]]; then
  echo ". Using existing service principal"
else
  echo '. Creating service principal'
  APP_SP=$(az ad sp create --id "$APP_ID")
fi

echo '== Searching app permissions for Azure Management Service'
AVAILABLE_PERMISSION=$(az ad app permission list-grants --show-resource-name --query "[?resourceDisplayName=='Windows Azure Service Management API'] | [?expiryTime > '$DATE']" | jq '.[0]')

API_PERMISSION_ID=$(jq -r '.resourceId' <<< "$AVAILABLE_PERMISSION")
echo ". Permission id: $API_PERMISSION_ID"

echo '== Checking Exposed Permissions on app'
EXPOSED_PERMISSIONS=$(az ad sp show --id "$APP_ID" | jq '.oauth2Permissions')
echo "$EXPOSED_PERMISSIONS"

EXPOSED_PERMISSION_ID=$(jq -r '.[0].id' <<< "$EXPOSED_PERMISSIONS")
echo ". Oauth2 Permission id: $EXPOSED_PERMISSION_ID"

echo '== Checking Added permissions of the app'
ADDED_PERMISSIONS=$(az ad app permission list --id "$APP_ID")

if [[ "$ADDED_PERMISSIONS" == '[]' ]]; then
  echo '. Adding permission to the app'
  az ad app permission add --id "$APP_ID" --api "$API_PERMISSION_ID" --api-permissions "$EXPOSED_PERMISSION_ID=Scope"

  echo '. Granting Permissions to app'
  az ad app permission grant --id "$APP_ID" --api "$API_PERMISSION_ID" --expires 1000
fi

# assign roles to the apps
echo '== Assigning roles to the app'
sleep 8s # a new service principal is not usable for role assignment instantly, neither after couple of seconds.. :)

echo '. Assigning Reservation Purchaser role to app'
az role assignment create --assignee "$APP_ID" --role 'Reservation Purchaser' -o none

ROLE_NAME="CloudAdminService"

ROLE_DEFINITION_JSON="{
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
ROLE_DEFINITIONS=$(az role definition list --name "$ROLE_NAME")

if [[ "$ROLE_DEFINITIONS" != '[]' ]]; then
  ROLE=$(jq '.[0]' <<< "$ROLE_DEFINITIONS")
  NEW_ACTIONS=$(jq '.Actions' <<< "$ROLE_DEFINITION_JSON")
  NEW_NOT_ACTIONS=$(jq '.NotActions' <<< "$ROLE_DEFINITION_JSON")
  UPDATED_ROLE=$(jq ".permissions[0].actions = $NEW_ACTIONS" <<< "$ROLE")
  UPDATED_ROLE=$(jq ".permissions[0].notActions = $NEW_NOT_ACTIONS" <<< "$UPDATED_ROLE")
  echo ". Updating existing custom role with defined Actions for CloudAdmin"
  az role definition update --role-definition "$UPDATED_ROLE" -o none
else
  echo '. Creating custom role for CloudAdmin'
  az role definition create --role-definition "$ROLE_DEFINITION_JSON" -o none
fi

echo '. Assigning custom role to app'
az role assignment create --assignee "$APP_ID" --role "$ROLE_NAME" -o none

echo "--------------------------------------------------------------------------------"

echo

echo "Save and use the following json to onboard credentials into CloudAdmin"
cat << EOF
{
  "subscriptionId": "$SELECTED_SUBSCRIPTION_ID",
  "tenantId": "$(echo "$SELECTED_SUBSCRIPTION" | jq -r '.tenantId')",
  "clientId": "$APP_ID",
  "clientSecret": "$APP_SECRET"
}
EOF
