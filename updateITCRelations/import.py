import json 
import requests 
import csv
import os
import logging


logging.basicConfig(level=logging.INFO)

#Request timeout
TIMEOUT = 20

#API token and subdomain set as env variables
LEANIX_API_TOKEN = os.getenv('LEANIX_API_TOKEN')
LEANIX_SUBDOMAIN = os.getenv('LEANIX_SUBDOMAIN')

LEANIX_AUTH_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net/services/mtm/v1/oauth2/token' 
LEANIX_REQUEST_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net/services/pathfinder/v1/graphql'

IMPORT_FILE = os.getenv('IMPORT_FILE')


#LOGIC
# Get the bearer token - see https://dev.leanix.net/v4.0/docs/authentication
def get_bearer_token(auth_url, api_token):
    """Function to retrieve the bearer token for authentication

    Args:
        auth_url (str): URL to retrieve the bearer token from
        api_token (str): The api-token to authenticate with

    Returns:
        dict: Dictionary containing the bearer token
    """
    if not LEANIX_API_TOKEN:
        raise Exception('A valid token is required')
    response = requests.post(auth_url, auth=('apitoken', api_token),
                             data={'grant_type': 'client_credentials'},
                             timeout=TIMEOUT)
    response.raise_for_status() 
    access_token = response.json()['access_token']
    auth_header = 'Bearer ' + access_token
    header = {'Authorization': auth_header}
    return header


# General function to call GraphQL given a query
def call(query, header, request_url):
    """Function that allows the user to perform graphql queries.

    Args:
        query (str): Query the user wants to perform on his workspace.

    Returns:
        str: JSON response string for the given query.
    """
    data = {"query" : query}
    json_data = json.dumps(data)
    response = requests.post(url=request_url, headers=header, data=json_data, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def createRelations(mapping):
  for key, value in mapping.items():
    idx = 1
    patches = []
    for v in set(value):
      patches.append("{op: add, path: \"/relToRequiredBy/new_" + str(idx) +"\", value: \"{\\\"factSheetId\\\": \\\"" + v + "\\\"}\"}")
      idx = idx + 1
    logging.info(patches)
    updateRelations(key, ",".join(patches))

def deleteRelations(id, relations):
  patches = []
  logging.info(relations)
  for v in relations:
    patches.append("{op: remove, path: \"/relToRequiredBy/" + str(v) +"\"}")
  logging.info(patches)
  updateRelations(id, ",".join(patches))
  exit

# Function to create a relation between Application and IT Component with the costs attribute
def updateRelations(itc, patches, header) :
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
  logging.info("Update relations for: " + itc)
  logging.info(call(query, header, LEANIX_REQUEST_URL))

def deleteExistingRelations(header):
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
  response = call(query, header, LEANIX_REQUEST_URL)
  for itcNode in response['data']['allFactSheets']['edges']:
    itcId = itcNode['node']['id']
    mapping = []
    for relationNode in itcNode['node']['relToRequiredBy']['edges']:
      relation = relationNode['node']
      refItcId = relationNode['node']['id']
      mapping.append(refItcId)
    deleteRelations(itcId, mapping)  


# Start of the main logic
try:
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, IMPORT_FILE)
except ValueError:
    logging.error('Failed to parse file input')


try:
    header = get_bearer_token(LEANIX_AUTH_URL, LEANIX_API_TOKEN)
except Exception as e:
    logging.error(f'Error while authenticating: {e}')

with open(filename) as df:
  try:
    logging.info(f'Parsing csv file: {df.name}')
    reader = csv.DictReader(df, delimiter=';')

  except Exception as e:
    logging.error(f'Failed to load csv file: {e}')

  mapping = {}

  try:
    for row in reader:
      if row['LeanIX_ID_SPV'] in mapping:      
        mapping[row['LeanIX_ID_SPV']].append(row['LeanIX_ID_LS'])
      else:
        mapping[row['LeanIX_ID_SPV']] = [row['LeanIX_ID_LS']]   

    createRelations(mapping)
  except Exception as e:
    logging.error(f'Erro while creating relations: {e}')
