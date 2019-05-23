import json 
import requests 
import csv
import os
from chameleon import PageTemplateLoader

templates = PageTemplateLoader(os.path.join(os.path.dirname(__file__), "templates"))

api_token = ''
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

query = """
{
  allFactSheets(factSheetType: Application) {
    edges {
      node {
        id
        displayName
        ... on Application {
          relApplicationToBusinessCapability {
            edges {
              node {
                id
                factSheet {
                  id
                  displayName
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

addedBcs = []
factSheets = []
relations = []
seq = 1
leftApp = 0
leftBC = 0

for appNode in response['data']['allFactSheets']['edges']:
  factSheets.append({
    'name': appNode['node']['displayName'], 
    'id': appNode['node']['id'], 
    'geometry': 'Left=' + str(leftApp) + ';Top=100;Right='+ str((leftApp+100)) +';Bottom=171;', 
    'seqno': seq})
  seq += 1
  leftApp += 200

  for relNode in appNode['node']['relApplicationToBusinessCapability']['edges']:
    bc = relNode['node']['factSheet']
    if (bc['id'] not in addedBcs):
      addedBcs.append(bc['id'])
      factSheets.append({
        'name': bc['displayName'], 
        'id': bc['id'], 
        'geometry': 'Left=' + str(leftBC) + ';Top=300;Right='+ str((leftBC+100)) +';Bottom=371;', 
        'seqno': seq})
      seq += 1
      leftBC += 200

    relations.append({
      'id': relNode['node']['id'],
      'src': appNode['node']['id'],
      'target': bc['id']
    } 
  )
  

#factSheets =  [
#    {'name': 'Example_Applications_R_D', 'id': 'EAID_DB2F55F8_F0C1_40e2_8684_81D96DFDF40C', 'geometry': 'Left=0;Top=100;Right=100;Bottom=171;', 'seqno': '1'}, 
#    {'name': 'Capabilities_R_D', 'id': 'EAID_E7199150_6695_4e5d_8C11_7A4607CA8B3A', 'geometry': 'Left=200;Top=100;Right=300;Bottom=171;', 'seqno': '2'},
#    {'name': 'Capabilities_HR', 'id': 'EAID_E7199150_6695_4e5d_8C11_7A4607CA8B3B', 'geometry': 'Left=400;Top=100;Right=500;Bottom=171;', 'seqno': '3'}
  
#  ]
#relations = [
#    {'id': 'EAID_6029C242_C653_4c70_81CA_A179D61B411B', 'src': 'EAID_DB2F55F8_F0C1_40e2_8684_81D96DFDF40C', 'target': 'EAID_E7199150_6695_4e5d_8C11_7A4607CA8B3A'},
#    {'id': 'EAID_6029C242_C653_4c70_81CA_A179D61B411C', 'src': 'EAID_DB2F55F8_F0C1_40e2_8684_81D96DFDF40C', 'target': 'EAID_E7199150_6695_4e5d_8C11_7A4607CA8B3B'}
#  ]   

template = templates['sparx.pt']
print (template(factSheets=factSheets,relations=relations))
