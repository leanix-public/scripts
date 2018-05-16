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
  print json_data
  response = requests.post(url=request_url, headers=header, data=json_data)
  response.raise_for_status()
  return response.json()

def createRelations(mapping):
  for key, value in mapping.items():
    idx = 1
    patches = []
    for v in set(value):
      patches.append("{op: add, path: \"/relToRequiredBy/new_" + str(idx) +"\", value: \"{\\\"factSheetId\\\": \\\"" + v + "\\\"}\"}")
      idx = idx + 1
    print patches
    updateRelations(key, ",".join(patches))

def deleteRelations(id, relations):
  patches = []
  print relations
  for v in relations:
    patches.append("{op: remove, path: \"/relToRequiredBy/" + str(v) +"\"}")
  print patches
  updateRelations(id, ",".join(patches))
  exit

# Function to create a relation between Application and IT Component with the costs attribute
def updateRelations(itc, patches) :
  query = """
     mutation {
      updateFactSheet(id: "%s", 
                      patches: [%s]) {
        factSheet {
          id
        } 
      }
    }
  """ % (itc, patches)
  print "Update relations for: " + itc 
  print call(query)

def deleteExistingRelations():
  query = """
{
  allFactSheets(filter: {facetFilters: [{facetKey: "FactSheetTypes", keys: ["ITComponent"]}, {facetKey: "relITComponentToTechnologyStack", keys: ["27c1158c-6ea6-4ab3-90e6-fe16dafa8e42"]}]}) {
    edges {
      node {
        id
        ... on ITComponent {relToRequiredBy {edges {node {id factSheet {id}}}}}
      }
    }
  }
}

  """
  response = call(query)
  for itcNode in response['data']['allFactSheets']['edges']:
    itcId = itcNode['node']['id']
    mapping = []
    for relationNode in itcNode['node']['relToRequiredBy']['edges']:
      relation = relationNode['node']
      refItcId = relationNode['node']['id']
      mapping.append(refItcId)
    deleteRelations(itcId, mapping)  


# Start of the main logic

# 1. Read the input as a CSV
df = pd.read_csv('import.csv', sep=';')

#deleteExistingRelations()

mapping = {}

for index, row in df.iterrows():
  if row['LeanIX_ID_SPV'] in mapping:      
    mapping[row['LeanIX_ID_SPV']].append(row['LeanIX_ID_LS'])
  else:
    mapping[row['LeanIX_ID_SPV']] = [row['LeanIX_ID_LS']]   

createRelations(mapping)
