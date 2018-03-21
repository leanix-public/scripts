import json 
import requests 
import pandas as pd

api_token = '<API-TOKEN>'
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

# Read all existing IT Components
def getIds():
  query = """
{
  allFactSheets(factSheetType: ITComponent) {
    edges {
      node {
        ... on ITComponent {
          documents {
            edges {
              node {
                id
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
  ids = []
  for itcNode in response['data']['allFactSheets']['edges']:
    for documentNode in itcNode['node']['documents']['edges']:
      docId = documentNode['node']['id']
      ids.append(docId)      
  return ids

# Delete the document
def deleteDocument(id):
  query = """
    mutation {
      deleteDocument(id: "%s") {
        id
      }
    } 
  """ % (id)
  print "delete " + id
  response = call(query)

# Start of the main program

ids = getIds()
for id in ids:
  deleteDocument(id)

