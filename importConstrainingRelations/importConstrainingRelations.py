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


def createBCRelation(app, bc, header) :
  """Create relation to business capability.

  Args:
      app (str): ID of the application the relation originates from.
      bc (str): ID of the business application the relation points to.
      header (dict): Authorization header.
  """  
  query = """
    mutation {
      updateFactSheet(id: "%s", 
                      patches: [{op: add, path: "/relApplicationToBusinessCapability/new_1", value: "{\\\"factSheetId\\\": \\\"%s\\\"}"}]) {
        factSheet {
          id
        } 
      }
    }
  """ % (app, bc)
  logging.info("Create app - bc relation: " + app + "->" + bc)
  call(query, header, LEANIX_REQUEST_URL)

def createUGRelation(app, bc, header) :
  """Create relation to user group.

  Args:
      app (str): ID of the application the relation originates from.
      bc (str): ID of the user group the relation points to.
      header (dict): Authorization header.
  """  
  query = """
    mutation {
      updateFactSheet(id: "%s", 
                      patches: [{op: add, path: "/relApplicationToUserGroup/new_1", value: "{\\\"factSheetId\\\": \\\"%s\\\"}"}]) {
        factSheet {
          id
        } 
      }
    }
  """ % (app, bc)
  logging.info("Create app - ug relation: " + app + "->" + bc)
  call(query, header, LEANIX_REQUEST_URL)

def createProcRelation(app, bc, header) :
  """Create relation to process.

  Args:
      app (st): ID of the application the relation originates from
      bc (st): ID of the process the relation points to.
      header (dict): Authorization header
  """  
  query = """
    mutation {
      updateFactSheet(id: "%s", 
                      patches: [{op: add, path: "/relApplicationToProcess/new_1", value: "{\\\"factSheetId\\\": \\\"%s\\\"}"}]) {
        factSheet {
          id
        } 
      }
    }
  """ % (app, bc)
  logging.info("Create app - bc relation: " + app + "->" + bc)
  call(query, header, LEANIX_REQUEST_URL)

def createConstraint(fs, constrainedType, constrainedId, constrainingType, constrainingId, header) :
  """_summary_

  Args:
      fs (_type_): _description_
      constrainedType (_type_): _description_
      constrainedId (_type_): _description_
      constrainingType (_type_): _description_
      constrainingId (_type_): _description_
      header (_type_): _description_
  """  
  query = """
    mutation {
      createRelationConstraint(factSheetId: "%s", constrainedRelationType: "%s", constrainedRelationTargetFactSheetId: "%s", constrainingRelationType: "%s", constrainingRelationTargetFactSheetId: "%s")
      {  
       id
      }
    }
  """ % (fs, constrainedType, constrainedId, constrainingType, constrainingId)
  logging.info(call(query, header, LEANIX_REQUEST_URL))

def deleteConstraint(fs, constrainedType, constrainedId, constrainingType, constrainingId, header) :
  """_summary_

  Args:
      fs (_type_): _description_
      constrainedType (_type_): _description_
      constrainedId (_type_): _description_
      constrainingType (_type_): _description_
      constrainingId (_type_): _description_
      header (_type_): _description_
  """  
  query = """
    mutation {
      deleteRelationConstraint(factSheetId: "%s", constrainedRelationType: "%s", constrainedRelationTargetFactSheetId: "%s", constrainingRelationType: "%s", constrainingRelationTargetFactSheetId: "%s")
      {  
       id
      }
    }
  """ % (fs, constrainedType, constrainedId, constrainingType, constrainingId)
  logging.info(call(query, header, LEANIX_REQUEST_URL))

def deleteConstraints(rel, header) :
  """Deletes the constraining relation.

  Args:
      rel (str): ID of the relation that is to be deleted.
      header (dict): Authorization header.
  """  
  query = """
  {
    allFactSheets(factSheetType: Application) {
    edges { node { id 
      ... on Application {
        relApplicationToProcess {
          edges {
            node {
              factSheet {id}
              constrainingRelations {
                relations {
                  factSheet {
                    id
                  }
                }
              }
            }
          }
        }
      }
    }}}
  }
  """
  response = call(query, header, LEANIX_REQUEST_URL)
  logging.info(response)
  for appNode in response['data']['allFactSheets']['edges']:
    appId = appNode['node']['id']
    logging.info(appId)
    for relationNode in appNode['node'][rel]['edges']:
      bcId = relationNode['node']['factSheet']['id']
      for constraint in relationNode['node']['constrainingRelations']['relations']:
        logging.info(deleteConstraint(appId, rel, bcId, 'relApplicationToUserGroup', constraint['factSheet']['id']))

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

# 1. Read the input as a CSV
with open(filename) as df:
  try:
      logging.info(f'Parsing csv file: {df.name}')
      reader = csv.DictReader(df, delimiter=';')  
  except Exception as e:
      logging.error(f'Failed to load csv file: {e}')

  #getConstraints()

  # 4. Create the relations based on the saved ids
  for row in reader:
   # if row['bc'] == row['bc']:
   #   createBCRelation(row['app'], row['bc'])
   # if row['ug'] == row['ug']:
   #   createUGRelation(row['app'], row['ug'])
    if row['bc'] == row['bc'] and row ['ug'] == row['ug']:
      createConstraint(row['app'], 'relApplicationToBusinessCapability', row['bc'], 'relApplicationToUserGroup', row['ug'], header)
    if row['process'] == row['process'] and row ['ug'] == row['ug']:
      createConstraint(row['app'], 'relApplicationToProcess', row['process'], 'relApplicationToUserGroup', row['ug'], header)
    if row['process'] == row['process'] and row ['bc'] == row['bc']:
      createConstraint(row['app'], 'relApplicationToProcess', row['process'], 'relApplicationToBusinessCapability', row['bc'], header)
    if row['process'] != row['process'] and row ['bc'] != row['bc'] and row['ug'] == row['ug']:
       createUGRelation(row['app'], row['ug'], header)
    if row['process'] != row['process'] and row ['bc'] == row['bc'] and row['ug'] != row['ug']:
       createBCRelation(row['app'], row['bc'], header)
    if row['process'] == row['process'] and row ['bc'] != row['bc'] and row['ug'] != row['ug']:
       createProcRelation(row['app'], row['process'], header)
