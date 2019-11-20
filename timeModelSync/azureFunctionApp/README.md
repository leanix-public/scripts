# Azure function to update Time Tag values on Application factsheets automatically
This projects provides they setup for an Azure Function App that listenes to LeanIX' FACT_SHEET_UPDATED events and updates the Time Tag on the factsheet according to the values of Functional Fit and Technical Fit. 

For an overview of the general functionality of the code please refer to: ../python/README.md

## Requirements
1. All requirements from ../python/README.md
2. Azure environment that can host Function Apps with Python.
3. Python 3.6.5 

## Setup
1. Clone the Repository
```
git clone git@github.com:leanix-public/scripts.git
cd timeModelSync/azureFunctionApp/timeModelSync
```
2. Create an Azure Function App on your Azure Environment
```
az functionapp create --resource-group myResourceGroup --consumption-plan-location westeurope \
--name timeModelSync --storage-account  <STORAGE_NAME> --runtime python
```
3. Deploy our project to your environment
```
func azure functionapp publish timeModelSync
```
Copy the Invoke URL that is posted in your console after the successfull deployment.

4. Setup a webhook subscription in your LeanIX workspace
(How to crate a webhook: https://dev.leanix.net/docs/webhooks)

Create a webhook subscription for the events: ```FACT_SHEET_CREATED``` and ```FACT_SHEET_UPDATED```.
Set type to ```PUSH````
Paste the invoke url of your Azure function into the target url field.
Grab the callback function from callback.js and paste it to the callback field. 
Select ```Ignore Errors```. 
Save. 

5. Set the Environment variables on your Azure environment

a. Save your host
Create an environment variable in your Azure portal called ```HOST ``` and set it to your host (e.g. app.leanix.net)

b. Save your tag ids for the time tag group. 
Paste the following JSON into an environment variable called ```TAG_MAPPING``` with the correct ids for your workspace:
```
{
    "tolerate": "<tag id>",
    "invest": "<tag id>",
    "migrate": "<tag id>",
    "eliminate": "<tag id>"
}
```

c. Save you API token
To save your API token for a live environment LeanIX advises you to use the Microsoft KeyVault (https://azure.microsoft.com/de-de/services/key-vault/).
Create a link to the Key Vault from an environment variable called: ```DEMO_TOKEN```

You are all set!
