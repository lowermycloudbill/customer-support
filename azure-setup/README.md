## Azure Setup

In order to properly setup Azure to work with CloudAdmin, follow these instructions:
1. In your Azure Portal, go to your *Azure Active Directory*
2. Go to *App registrations*
3. In App Registrations, *Add New Registration*.
4. When adding a new registration, fill the API name as **CloudAdmin** and hit *Register*.
5. After registering, make a note of the **Application Id (client id)**, and the **Directory Id (tenant id)**, and go to *Certificates & Secrets*
6. Click *Create New Secret*.
7. Add a description for the new client secret and click *Add*. After creating the new client secret, **make a note of the id** because it will not be visible anymore.
8. Then go to *API Permissions*.
9. On API permissions, add a *New Permission*.
10. Select *Azure Service Management*
11. Tick **User Impersonation** checkbox and click *Add Permission*.
12. Now go to *All Services and to Subscriptions*
13. Click on the Subscription desired that you want to use with CloudAdmin, and make a **note of the Subscription Id**. 
14. Once in your Subscription, go to *Access Control (IAM)*
15. Click on *Add* and click on *Add Role Assignment*.
16. Look for and select the Role **Reservation Purchaser**, and then search and select the App you created in Step 4, and click *Save*.
17. After saving, go into *Access Control (IAM)* once again.
18. Click *Add* and click on *Add a Custom Role*.
19. Go to the tab named *JSON*, click on *Edit* and paste the following json:
 
```json{
   "properties": {
       "roleName": "CloudAdminService",
       "description": "Required permissions for Cloudadmin Services",
       "assignableScopes": [
           "<subscription id>"
       ],
       "permissions": [
           {
               "actions": [
                    "*/read",
                    "Microsoft.Compute/virtualMachines/start/action",
                    "Microsoft.Compute/virtualMachines/restart/action",
                    "Microsoft.Compute/virtualMachines/powerOff/action",
                    "Microsoft.Compute/disks/delete",
                    "Microsoft.Compute/snapshots/delete",
                    "Microsoft.Sql/servers/databases/resume/action",
                    "Microsoft.Sql/servers/databases/pause/action",
                    "Microsoft.Network/loadBalancers/delete",
                    "Microsoft.Network/publicIPAddresses/delete"
               ],
               "notActions": [],
               "dataActions": [],
               "notDataActions": []
           }
       ]
   }
}
```
20. Make sure to replace `<subscription id>` in the json with your Subscription Id.
21. *Save* the changes and click *Review + Create*. 
22. Finally, click *Create*.
23. Click on *Add* and click on *Add Role Assignment*.
24. Look for and select the Role **CloudAdminServices**, and then search and select the App you created in Step 4, and click *Save*.
25. Now go to *cloudadmin.io* and on Azure Credentials page, add the **subscription id**, the **tenant id**, the **client id** and the **client secret** as a new credential.
