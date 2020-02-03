import json 
import requests 
import pandas as pd

api_token = 'a1b5c400-f9bc-487a-bf6f-0d5072f70df1'
auth_url = 'https://app.leanix.net/services/mtm/v1/oauth2/token' 
request_url = 'https://eu.leanix.net/services/pathfinder/v1/graphql'

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
def getRelations():
  query = """
  {
    allFactSheets(factSheetType: BusinessCapability) {
      edges {
        node {
          id
          ... on Application {
            relApplicationToITComponent {
              edges {
                node {
                  id
                  factSheet {
                    id
                  }
                }
              }
            }
          }
        }
      }
    }
  }
  """
  response = call(query)
  apps = {}
  for appNode in response['data']['allFactSheets']['edges']:
    appId = appNode['node']['id']
    apps[appId] = {}
    for relationNode in appNode['node']['relApplicationToITComponent']['edges']:
      relationId = relationNode['node']['id']
      itcId = relationNode['node']['factSheet']['id']
      apps[appId][itcId] = relationId
  return apps

# Update the costs attribute on the existing relation
def updateCosts(app, itc, rel, costs) :
  query = """
    mutation {
      updateFactSheet(id: "%s", 
                      patches: [{op: replace, path: "/relApplicationToITComponent/%s", value: "{\\\"factSheetId\\\": \\\"%s\\\",\\\"costTotalAnnual\\\": %s}"}]) {
        factSheet {
          id
        } 
      }
    }
  """ % (app, rel, itc, costs)
  print("Update costs: " + app + "->" + itc + " = " + str(costs))
  response = call(query)
  print(response)

# Start of the main program

# 1. Read the input
df = pd.read_csv('exampleUpdate.csv')

# 2. Get the existing relations from LeanIX
apps = getRelations()

# 3. Update the cost attribute for each row
for index, row in df.iterrows():
  updateCosts(row['app'], row['itc'], apps[row['app']][row['itc']], row['costs'])

