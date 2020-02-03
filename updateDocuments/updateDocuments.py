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

# Read all existing IT Components
def getIds():
  query = """
{
  allFactSheets {
    edges {
      node {
          documents {
            edges {
              node {
                id
                url
              }
            }
        }
      }
    }
  }
}
  """
  response = call(query)
  ids = {}
  for itcNode in response['data']['allFactSheets']['edges']:
    for documentNode in itcNode['node']['documents']['edges']:
      docId = documentNode['node']['id']
      docUrl = documentNode['node']['url']
      if (docUrl.startswith(" ")):
        print(docUrl)
        ids.update({docId: docUrl})      
  return ids

# Delete the document
def updateDocument(id,url):
  query = """
    mutation {
      updateDocument(id: "%s", patches: [{path: "/url", op: replace, value: "%s"}]) {
        id
      }
    } 
  """ % (id, url)
  print("update " + id + " " +  url)
  response = call(query)
  print(response)

# Start of the main program

ids = getIds()
for id, url in ids.items():
  updateDocument(id, url[1:])

