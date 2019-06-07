import json 
import requests 
import pandas as pd
import math


mtm_base_url = 'https://svc.leanix.net/services/mtm/v1' 
pathfinder_base_url = 'https://adidas.leanix.net/services/pathfinder/v1'

#Authorization
def getApiToken():
  with open('../access.json') as json_file:  
    data = json.load(json_file)
    return data['apitoken']

def getAccessToken(api_token):
  #different than callPost since it needs to send the auth_header
  response = requests.post(mtm_base_url+"/oauth2/token", auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'})
  response.raise_for_status() 
  access_token = response.json()['access_token']
  return access_token

def getHeader(access_token):
  return {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}

# General function to call GraphQL given a query
def call(query, access_token):
  data = {"query" : query}
  json_data = json.dumps(data)
  response = requests.post(url=pathfinder_base_url+ '/graphql', headers=getHeader(access_token), data=json_data)
  response.raise_for_status()
  return response.json()

# Read all existing Application - IT Component relations
def getAllApps(access_token):
  query = """
  {
    allFactSheets(factSheetType: BusinessCapability) {
      edges {
        node {
          id
          tags { id name tagGroup {name} }
        }
      }
    }
  }
  """
  response = call(query, access_token)
  return response['data']['allFactSheets']['edges']
 
# Start of the main program
access_token = getAccessToken(getApiToken())
df = pd.read_csv('mapping.csv', sep=';')

apps = getAllApps(access_token)
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
    response = call(query,access_token)
    print (response)

