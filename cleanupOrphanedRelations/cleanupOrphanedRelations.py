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

def cleanupRelations():
  query = """
    {
      allFactSheets(filter: {facetFilters: [{facetKey: "FactSheetTypes", keys: ["Application"]}, {facetKey: "TrashBin", keys: ["archived"]}]}) {
        totalCount
        edges {
          node {
            ... on Application {
              id
              name
              rev
              status
              relApplicationToProcess {
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
  
  for appNode in response['data']['allFactSheets']['edges']:
    appId = appNode['node']['id']
    relations = appNode['node']['relApplicationToProcess']['edges']

    if (len(relations) > 0):
      patches = ["{op: replace, path: \"/status\", value: \"ACTIVE\"}"]
      for relation in relations:
        patches.append("{op: remove, path: \"/relApplicationToProcess/" + relation['node']['id'] +"\"}")
      update(appId, "Undelete for cleanup", ",".join(patches))
      update(appId, "Redelete", "{op: replace, path: \"/status\", value: \"ARCHIVED\"}")
    
def update(app, comment, patches) :
  query = """
    mutation {
      updateFactSheet(id: "%s", comment: "%s", patches: [%s], validateOnly: false) {
        factSheet {
          id
        }
      }
    }
  """ % (app, comment, patches)
  print comment + ":" + app
  response = call(query)
  print response

# Start of the main program
cleanupRelations()
