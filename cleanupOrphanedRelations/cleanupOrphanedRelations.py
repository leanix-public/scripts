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


def cleanupRelations(header):
  """Queries orphaned relations and queues them up for cleanup.

  Args:
      header (dict): Authorization header.
  """  
  query = """
    {
      allFactSheets(filter: {facetFilters: [{facetKey: "FactSheetTypes", keys: ["Application"]}, {facetKey: "TrashBin", keys: ["archived"]}]}) {
        totalCount
        edges {
          node {
            ... on Application {
              id
              name
              rev
              status
              relApplicationToProcess {
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
  response = call(query, header)
  
  for appNode in response['data']['allFactSheets']['edges']:
    appId = appNode['node']['id']
    relations = appNode['node']['relApplicationToProcess']['edges']

    if (len(relations) > 0):
      patches = ["{op: replace, path: \"/status\", value: \"ACTIVE\"}"]
      for relation in relations:
        patches.append("{op: remove, path: \"/relApplicationToProcess/" + relation['node']['id'] +"\"}")
      update(appId, "Undelete for cleanup", ",".join(patches), header)
      update(appId, "Redelete", "{op: replace, path: \"/status\", value: \"ARCHIVED\"}", header)
    

def update(app, comment, patches, header) :
  """Puts together query to archive orphaned relations.

  Args:
      app (str): ID of the application that contains the targeted relation.
      comment (str): Comment set during the cleanup query.
      patches (str): Patch that cleans the orphaned relation up.
      header (dict): Authorization header.
  """  
  query = """
    mutation {
      updateFactSheet(id: "%s", comment: "%s", patches: [%s], validateOnly: false) {
        factSheet {
          id
        }
      }
    }
  """ % (app, comment, patches)
  print(comment + ":" + app)
  response = call(query, header, LEANIX_REQUEST_URL)
  print(response)


# Start of the main program
def main():
  try:
    header = get_bearer_token(LEANIX_AUTH_URL, LEANIX_API_TOKEN)
  except Exception as e:
    logging.error(f'Error while authenticating: {e}')

  try:
    cleanupRelations(header)
  
  except Exception as e:
     logging.error(f'Error while processing relations: {e}')


if __name__ == "__main__":
    main()
