import json 
import requests 
import pandas as pd

# In order to break the quality seal we do not have a direct query. Hence the option available is to use a specific field
# on a FactSheet and update it using a member.
# 1. Set the api_token in line 10 of a Technical user who has MEMBER role
# 2. Modify the request_url as per your instance i.e. customer.leanix.net
# 3. Modify the factSheetType in order to update all the FactSheets, if you want to update the specific FactSheets adjust the query in getAllApps()
# 4. Modify the field to be updated as per the requirement in updateFactSheet()
#
api_token = 'apiTokenHere'
auth_url = 'https://app.leanix.net/services/mtm/v1/oauth2/token' 
request_url = 'https://app.leanix.net/services/pathfinder/v1/graphql' 
factSheetType = "Application"

# Get the bearer token - see https://dev.leanix.net/v4.0/docs/authentication
response = requests.post(auth_url, auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'})
response.raise_for_status() 
access_token = response.json()['access_token']
auth_header = 'Bearer ' + access_token
header = {'Authorization': auth_header}

# General function to call GraphQL given a query
def call(query):
  data = {"query" : query}
  json_data = json.dumps(data)
  response = requests.post(url=request_url, headers=header, data=json_data)
  response.raise_for_status()
  return response.json()

# Read all existing FactSheets as per factSheetType - Modify this to break the quality Seal as per requirement.
def getAllApps():
  query = """
  {
    allFactSheets(factSheetType: %s) {
      edges {
        node {
          id
        }
      }
    }
  }
  """ % (factSheetType)
  response = call(query)
  apps = []
  for appNode in response['data']['allFactSheets']['edges']:
    appId = appNode['node']['id']
    apps.append(appId)
  return apps

def updateFactSheet(app) :
  #Here we are updating a field alias , but Ideal will be to create a new field for this purpose and update the field  
  query = """
    mutation {
      updateFactSheet(id: "%s", 
                      patches: [{op: add, path: "/alias", value: "xx"}]) {
        factSheet {
          id
        } 
      }
    }
  """ % (app)
  response = call(query)
  print (response)

# Start of the main program

# 1. Get the existing factsheets from LeanIX
apps = getAllApps()
print (apps)

# 2. Update the quality sealfor each row
for app in apps:
  updateFactSheet(app)

