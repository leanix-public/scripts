import json 
import requests 
import csv
import os
import logging


"""
mtm_base_url = 'https://svc.leanix.net/services/mtm/v1' 
pathfinder_base_url = 'https://abc.leanix.net/services/pathfinder/v1'
"""


logging.basicConfig(level=logging.INFO)

#Request timeout
TIMEOUT = 20

#API token and subdomain set as env variables
LEANIX_API_TOKEN = os.getenv('LEANIX_API_TOKEN')
LEANIX_SUBDOMAIN = os.getenv('LEANIX_SUBDOMAIN')

LEANIX_AUTH_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net/services/mtm/v1' 
LEANIX_REQUEST_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net/services/pathfinder/v1'


#INPUT
mtm_base_url = LEANIX_AUTH_URL
pathfinder_base_url = LEANIX_REQUEST_URL
api_token = LEANIX_API_TOKEN


#Authorization
def getAccessToken(api_token):
  #different than callPost since it needs to send the auth_header
  response = requests.post(mtm_base_url+"/oauth2/token", auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'},
                         timeout=TIMEOUT)
  response.raise_for_status() 
  access_token = response.json()['access_token']
  return access_token

def getHeader(access_token):
  return {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}

# General function to call GraphQL given a query
def callGraphQL(query, access_token):
  #print("callGraphQl")
  data = {"query" : query}
  json_data = json.dumps(data)
  #print("request")
  response = requests.post(url=pathfinder_base_url + '/graphql', headers=getHeader(access_token), data=json_data, timeout=TIMEOUT)
  response.raise_for_status()
  #print("requested")
  return response.json()

def call(url, access_token):
  response = requests.get(url=pathfinder_base_url + '/' + url, headers=getHeader(access_token), timeout=TIMEOUT)
  response.raise_for_status()
  return response.json()


# Read all existing Application - IT Component relations
# Comment from CHZ: while variables isn't needed in the query here,
# leaving it in the query so others know it's an option
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
  response = callGraphQL(query, access_token)
  return(response)
 

# Start of the main program
try:
  access_token = getAccessToken(api_token)
except Exception as e:
  logging.info(f'Error while retrieving authorization header: {e}')

with open('mapping.csv') as df:
  try:
    logging.info(f'Parsing csv file: {df.name}')
    reader = csv.DictReader(df, delimiter=';')
  except Exception as e:
    logging.error(f'Failed to load csv file: {e}')

  apps = getAllApps(access_token)
  for appNode in apps['data']['allFactSheets']['edges']:
    tags = list(map(lambda x: x['id'], appNode['node']['tags']))

    patches = []
    multiSelects = {}

    for row in reader:
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
    logging.info(query)
    response = callGraphQL(query, access_token)
    logging.info(response)
