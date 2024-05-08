import json 
import requests
import logging
import os


logging.basicConfig(level=logging.INFO)

#Request timeout
TIMEOUT = 20

#API token and subdomain set as env variables
LEANIX_API_TOKEN = os.getenv('LEANIX_API_TOKEN')
LEANIX_SUBDOMAIN = os.getenv('LEANIX_SUBDOMAIN')

LEANIX_AUTH_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net/services/mtm/v1/oauth2/token' 
LEANIX_REQUEST_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net/services/pathfinder/v1/graphql'

IMPORT_FILE = os.getenv('IMPORT_FILE')

FACTSHEET_TYPE = os.getenv('FACTSHEET_TYPE')
RELATIONSHIP = os.getenv('RELATIONSHIP')
CONSTRAINING_RELATIONSHIP = os.getenv('CONSTRAINING_RELATIONSHIP')


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


def createConstraint(fs, constrainedType, constrainedId, constrainingType, constrainingId, header) :
    """Creates a constraint.

    Args:
        fs (_type_): _description_
        constrainedType (_type_): _description_
        constrainedId (_type_): _description_
        constrainingType (_type_): _description_
        constrainingId (_type_): _description_
    """    
    query = """
      mutation {
        createRelationConstraint(factSheetId: "%s", constrainedRelationType: "%s", constrainedRelationTargetFactSheetId: "%s", constrainingRelationType: "%s", constrainingRelationTargetFactSheetId: "%s")
        {  
         id
         name
        }
      }
    """ % (fs, constrainedType, constrainedId, constrainingType, constrainingId)
    logging.info(call(query, header, LEANIX_REQUEST_URL))


def fixConstraints(header, fsType='Project', rel='relProjectToBusinessCapability', constrainingRel='relProjectToUserGroup') :
    """Mutation to fix the given constraining relation.

    Args:
        header (dict): Authorization header.
        fsType (str, optional): Factsheet type. Defaults to 'Project'.
        rel (str, optional): Relation to fix. Defaults to 'relProjectToBusinessCapability'.
        constrainingRel (str, optional): Name of the constraining relation. Defaults to 'relProjectToUserGroup'.
    """    
    query = """
    { allFactSheets(factSheetType: %s) {
        edges { node { 
          id 
          name 
          ... on %s {
            %s {edges { node { factSheet { id name}}}}
            %s {edges { node { factSheet { id name}}}}
          }
        }}
    }}""" % (fsType, fsType, rel, constrainingRel)
    
    response = call(query, header, LEANIX_REQUEST_URL)
    for fsNode in response['data']['allFactSheets']['edges']: # eg: Project
      fsId = fsNode['node']['id']
      fsName = fsNode['node']['name']
      for relFs in fsNode['node'][rel]['edges']: # eg: Business Capability
        relFsId = relFs['node']['factSheet']['id']
        relFsName = relFs['node']['factSheet']['name']
        for constrainRelFs in fsNode['node'][constrainingRel]['edges']: # eg: User Group
          constrainRelFsId = constrainRelFs['node']['factSheet']['id']
          constrainRelFsName = constrainRelFs['node']['factSheet']['name']
          print("""Creating constrinaning relation for '%s' between '%s' and '%s'""" %(fsName, relFsName, constrainRelFsName))
          createConstraint(fsId, rel, relFsId, constrainingRel, constrainRelFsId, header)

   
# Start of the main logic
try:
    header = get_bearer_token(LEANIX_AUTH_URL, LEANIX_API_TOKEN)
except Exception as e:
    logging.error(f'Error while authenticating: {e}')

try:
    fixConstraints(header, fsType=FACTSHEET_TYPE, rel=RELATIONSHIP, constrainingRel=CONSTRAINING_RELATIONSHIP)
except Exception as e:
    logging.error(f'Error while processing relation: {e}')
