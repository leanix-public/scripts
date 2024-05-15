import json
import requests
import base64
import click
import csv
import logging
import os


#Request timeout
TIMEOUT = 20

#API token and subdomain set as env variables
LEANIX_API_TOKEN = os.getenv('LEANIX_API_TOKEN')
LEANIX_SUBDOMAIN = os.getenv('LEANIX_SUBDOMAIN')

LEANIX_REQUEST_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net'
SERVICENOW_URL = os.getenv('SERVICENOW_URL')

IMPORT_FILE = os.getenv('IMPORT_FILE')

# Define Global variables here
# Required Global Variable : apiToken
apiToken = LEANIX_API_TOKEN
# Update the externalUrl with the ServiceInstance Name and tableName
# "https://<ServiceInstance>.service-now.com/nav_to.do?uri=<tableName>.do?sys_id="
externalUrl = SERVICENOW_URL
base_url = LEANIX_REQUEST_URL

def getAccessToken(api_token):
    """Retrieve access token.

    Args:
        api_token (str): API-Token to authenticate with.

    Returns:
        str: Access token.
    """    
    api_token = api_token
    auth_url = base_url+'/services/mtm/v1/oauth2/token'

    # Get the bearer token - see https://dev.leanix.net/v4.0/docs/authentication
    response = requests.post(auth_url, auth=('apitoken', api_token),
                             data={'grant_type': 'client_credentials'}, timeout=TIMEOUT)
    response.raise_for_status()
    access_token = response.json()['access_token']
    return access_token

# Function to decipher the access_token
def getAccessTokenJson(access_token):
    """Function to decipher the access_token.

    Args:
        access_token (str): Access token.

    Returns:
        str: Payload that contains the access token.
    """    
    payload_part = access_token.split('.')[1]
    # fix missing padding for this base64 encoded string.
    # If number of bytes is not dividable by 4, append '=' until it is.
    missing_padding = len(payload_part) % 4
    if missing_padding != 0:
        payload_part += '=' * (4 - missing_padding)
    payload = json.loads(base64.b64decode(payload_part))
    return payload

# runUpdate method to update ServiceNow ExternalId
def runUpdate(access_token):
    """Updates the ServiceNow id.

    Args:
        access_token (str): Access token.
    """    
    with open('ServiceNow.csv') as df:
        try:
            logging.info(f'Parsing csv file: {df.name}')
            reader = csv.DictReader(df, delimiter=';')

        except Exception as e:
            logging.error(f'Failed to load csv file: {e}')

    for row in reader:
        runMutation(row['id'], access_token,row['serviceNowExternalId'])

def runMutation(factSheetId, access_token, serviceNowExternalId):
    """Runs the actual mutation to update the ServiceNow ids.

    Args:
        factSheetId (str): Factsheet that contains the ServiceNow id.
        access_token (str): Access token.
        serviceNowExternalId (str): New id.
    """    
    status = "LINKED"
    serviceNowUrl = externalUrl+serviceNowExternalId
   # tags.append(tagId)
    #tags = list(dict.fromkeys(tags))
    #patches = ""
    #technopediaString = '{\\\"type\\\": \\\"ExternalId\\\",\\\"externalId\\\": \\\"'+ technopediaId +'\\\",\\\"comment\\\": \\\"This Fact Sheet was linked to an entry in Technopedia\\\",\\\"status\\\": \\\"LIFECYCLE_ONLY\\\"}'
    if(status == 'LINKED'):
        patches = "{op: replace, path: \"/serviceNowExternalId\", value: \"{\\\"type\\\": \\\"ExternalId\\\",\\\"externalId\\\": \\\""+ serviceNowExternalId +"\\\",\\\"externalVersion\\\": \\\"\\\",\\\"comment\\\": \\\"This Fact Sheet was linked to an entry in ServiceNow\\\",\\\"status\\\": \\\"LINKED\\\",\\\"externalUrl\\\": \\\""+ serviceNowUrl +"\\\",\\\"forceWrite\\\":true}\"}"
    query = """
    mutation{
        updateFactSheet(id: "%s",patches: [%s]) {
        factSheet {
        id
        }
        }
      }
    """ % (factSheetId, patches)
    response_mutation = call("query", query, access_token)
    logging.info(response_mutation)

# General function to call GraphQL given a query
def call(request_type, query, access_token):
    """Call GraphQL with a given query.

    Args:
        request_type (str): Type of query you want to perform.
        query (str): The query you want to perform.
        access_token (str): Access token.

    Returns:
        str: Response to the given query.
    """    
    auth_header = 'Bearer ' + access_token
    header = {'Authorization': auth_header}
    request_url = base_url+'/services/pathfinder/v1/graphql'
    data = {request_type: query}
    json_data = json.dumps(data)
    response = requests.post(url=request_url, headers=header, data=json_data, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()

# start of main program
if __name__ == '__main__':
    access_token = getAccessToken(apiToken)
    access_token_json = getAccessTokenJson(access_token)
    logging.info(access_token_json['principal']['username'])
    logging.info(access_token_json['principal']['permission']['workspaceName'])
    if click.confirm('Do you want to continue?', default=True):
      runUpdate(access_token)