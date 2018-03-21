import json 
import requests 
import pandas as pd

api_token = '<TOKEN>'
auth_url = 'https://app.leanix.net/services/mtm/v1/oauth2/token' 
request_url = 'https://app.leanix.net/services/pathfinder/v1/graphql' 

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

# Read all existing Application - IT Component relations
def getAllApps():
  query = """
  {
    allFactSheets(factSheetType: Application) {
      edges {
        node {
          id
        }
      }
    }
  }
  """
  response = call(query)
  apps = []
  for appNode in response['data']['allFactSheets']['edges']:
    appId = appNode['node']['id']
    apps.append(appId)
  return apps

def setQualitySeal(app) :
  query = """
    mutation {
      updateFactSheet(id: "%s", 
                      patches: [{op: add, path: "/qualitySeal", value: "approve"}]) {
        factSheet {
          id
        } 
      }
    }
  """ % (app)
  print "Set seal for: " + app
  response = call(query)
  print response

# Start of the main program

# 1. Get the existing factsheets from LeanIX
apps = getAllApps()
print apps

# 2. Update the quality sealfor each row
for app in apps:
  setQualitySeal(app)

