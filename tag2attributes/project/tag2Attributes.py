import json 
import requests 
import pandas as pd
import math
import json
from os import environ
import lxpy


mtm_base_url = 'https://svc.leanix.net/services/mtm/v1' 
pathfinder_base_url = 'https://adidas.leanix.net/services/pathfinder/v1'

# Authorization
config = lxpy.ClientConfiguration(
  base_url=environ.get('BASE_URL', 'us.leanix.net'),
  api_token=environ.get('API_TOKEN', 'YSCOXQbwROr8XMWGutW3NAhtpEsuKsWtH3JDPSX3')
)

# Setup for Pathfinder API
pathfinder = lxpy.Pathfinder(config)

# General function to call GraphQL given a query
def call(query):
  data = {"query" : query}
  response = pathfinder.graphql().process_graph_ql(data)
  # print(response)
  # import pdb; pdb.set_trace()
  return(response.to_dict())


# Read all existing Application - IT Component relations
# Comment from CHZ: while variables isn't needed in the query here,
# leaving it in the query so others know it's an option
def getAllApps():
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
  response = call(query)
  return(response)
 

# Start of the main program
# access_token = getAccessToken(getApiToken())
df = pd.read_csv('mapping.csv', sep=';')

apps = getAllApps()
for appNode in apps['data']['allFactSheets']['edges']:
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

