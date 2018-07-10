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

# Update the costs attribute on the existing relation
def setExternalId(app, signavioId) :
  query = """
    mutation {
      updateFactSheet(id: "%s", 
                      patches: [{op: replace, path: "/signavioGlossaryItemId", value: "{\\\"externalId\\\": \\\"%s\\\",\\\"forceWrite\\\": true}"}]) {
        factSheet {
          id
        } 
      }
    }
  """ % (app, signavioId)
  print "Update id: " + app + "->" + signavioId
  response = call(query)
  print response

# Start of the main program

# 1. Read the input
df = pd.read_csv('input.csv', sep=';')

# 2. Update the external Id
for index, row in df.iterrows():
  setExternalId(row['app'], row['signavioId'])

