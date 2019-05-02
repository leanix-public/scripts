import json 
import requests 
import pandas as pd
import math

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

# Read all existing Application - IT Component relations
def getAllApps():
  query = """
  {
    allFactSheets(factSheetType: Application) {
      edges {
        node {
          id
          tags { id name tagGroup {name} }
        }
      }
    }
  }
  """
  response = call(query)
  return response['data']['allFactSheets']['edges']
 
# Start of the main program
df = pd.read_csv('mapping.csv', sep=';')

apps = getAllApps()
for appNode in apps:

    tags = list(map(lambda x: x['id'], appNode['node']['tags']))
    
    patches = []
    multiSelects = {}

    for index, row in df.iterrows():
      if (row['Tag ID'] in tags):
        tags.remove(row['Tag ID'])

        if (row['Type'] == 'SINGLE_SELECT'):
          patches.append("{op: add, path: \"/" + row['Attribute'] + "\", value: \""+ row['Value'] + "\"}")
        elif (row['Type'] == 'MULTIPLE_SELECT'):
          if (row['Attribute'] not in multiSelects):
            multiSelects[row['Attribute']] = []
          multiSelects[row['Attribute']].append(row['Value'])

    for k, v in multiSelects.items():
      multiSelectString = ",".join(map( lambda x: '\\\"' + x + '\\\"', v))
      patches.append("{op: replace, path: \"/"+ k +"\", value: \"["+ multiSelectString +"]\"}")
 
    tagString = ",".join(map(lambda x: '{\\\"tagId\\\": \\\"' + x + '\\\"}', tags))
    patches.append("{op: replace, path: \"/tags\", value: \"["+ tagString + "]\"}")

    query = """
        mutation {
          updateFactSheet(id: "%s", patches: [%s]) {
            factSheet {
              id
            } 
          }
        }
      """ % (appNode['node']['id'], ",".join(patches))
    print (query)
    response = call(query)
    print (response)