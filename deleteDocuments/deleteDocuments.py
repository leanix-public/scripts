import json 
import requests 
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


# Read all existing IT Components
def getIds(header):
  """Retrieve ids from all existing IT Components.

  Args:
      header (dict): Authorization header.

  Returns:
      list: List of factsheet ids.
  """  
  query = """
  {
  allFactSheets(factSheetType: ITComponent) {
    edges {
      node {
        ... on ITComponent {
          documents {
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
  response = call(query, header, LEANIX_REQUEST_URL)
  ids = []
  for itcNode in response['data']['allFactSheets']['edges']:
    for documentNode in itcNode['node']['documents']['edges']:
      docId = documentNode['node']['id']
      ids.append(docId)      
  return ids

# Delete the document
def deleteDocument(id, header):
  query = """
    mutation {
      deleteDocument(id: "%s") {
        id
      }
    } 
  """ % (id)
  print("delete " + id)
  response = call(query, header, LEANIX_REQUEST_URL)
  logging.info(response)


# Start of the main program
try:
  header = get_bearer_token(LEANIX_AUTH_URL, LEANIX_API_TOKEN)
except Exception as e:
  logging.error(f'Error while authenticating: {e}')

try:
  ids = getIds()
  for id in ids:
    deleteDocument(id, header)

except Exception as e:
   logging.error(f'Error while parsing factsheets: {e}')
