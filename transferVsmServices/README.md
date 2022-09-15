# transferVsmService
This script is for transferring services from a pathfinder based VSM workspace to VSM.

# Running
python3 transferVsmServices --oldvsm_apitoken <api-token from a technical user old system> --newvsm_apitoken <api-token from a technical user new system>

# Troubleshooting
It could be necessary to update the following url's. Please make sure you have the correct URL's set for your specific Workspaces. de-svc / demo-de might differ.
-auth_url = 'https://de-svc.leanix.net/services/mtm/v1/oauth2/token'
-discovery_api_url = 'https://demo-de.leanix.net/services/vsm-collector/v1/item'
-graphql_url = "https://demo-de.leanix.net/services/pathfinder/v1/graphql"
