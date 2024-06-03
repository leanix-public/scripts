# Once you have the Info.csv ready with all the changes you can use this script to import the changes back.
# Please keep in mind if you have added certain attributes in the exportRelationship.py, also adapt this script per the need.
# This works by default in line with the ApplicationtoITRelationship and changes in Technical Fit.
# Changes required :-
# 1. Provide : apiToken and adapt the base_url as per your instance.
# 2. Modify the runUpdate as per the requirement.
# 3. Test the script in Sandbox and on a small amount of data before making the bulk changes.
# -*- coding: utf-8 -*-
"""Script for importing relations.

This script allows the user to import relations.
The necessary information is given in the import file.

Example:
    $ LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> IMPORT_FILE=<your input file> python importRelations.py

Global variables:
    TIMEOUT (int): Timeout for requests.
    LEANIX_API_TOKEN (str): API-Token to authenticate with.
    LEANIX_SUBDOMAIN (str): LeanIX subdomain.
    LEANIX_AUTH_URL (str): URL to authenticate against.
    LEANIX_REQUEST_URL (str): URL to send graphql requests to.
    IMPORT_FILE (str): Name of the import file.

"""

import json
import requests
import base64
import click
import csv
import os
import logging


"""
# Define Global variables here
# Required Global Variable : apiToken
apiToken = ""
# Update the Base URL of your LeanIX instance
base_url = 'https://demo-eu.leanix.net'
"""


logging.basicConfig(level=logging.INFO)

#Request timeout
TIMEOUT = 20

#API token and subdomain set as env variables
LEANIX_API_TOKEN = os.getenv('LEANIX_API_TOKEN')
LEANIX_SUBDOMAIN = os.getenv('LEANIX_SUBDOMAIN')

LEANIX_AUTH_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net/services/mtm/v1' 
LEANIX_REQUEST_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net'

IMPORT_FILE = os.getenv('IMPORT_FILE')


#INPUT
base_url = LEANIX_REQUEST_URL
apiToken = LEANIX_API_TOKEN


def getAccessToken(api_token):
    """Generates JSON from the access token.

    Args:
        access_token (str): Access token.
    Returns:
        str: Access token json.
    """  
    api_token = api_token
    auth_url = base_url+'/services/mtm/v1/oauth2/token'

    # Get the bearer token - see https://dev.leanix.net/v4.0/docs/authentication
    response = requests.post(auth_url, auth=('apitoken', api_token),
                             data={'grant_type': 'client_credentials'},
                             timeout=TIMEOUT)
    response.raise_for_status()
    access_token = response.json()['access_token']
    return access_token

# Function to decipher the access_token
def getAccessTokenJson(access_token):
    """Generates JSON from the access token.

    Args:
          access_token (str): Access token.
    Returns:
          str: Access token json.
    """  
    payload_part = access_token.split('.')[1]
    # fix missing padding for this base64 encoded string.
    # If number of bytes is not dividable by 4, append '=' until it is.
    missing_padding = len(payload_part) % 4
    if missing_padding != 0:
        payload_part += '=' * (4 - missing_padding)
    payload = json.loads(base64.b64decode(payload_part))
    return payload

# runUpdate method to update FactSheet
def runUpdate(access_token):
    """Runs an update for a factsheet.

    Args:
        access_token (str): Access token.
    """    
    try:
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, IMPORT_FILE)
    except ValueError:
        logging.error('Failed to parse file input')

    with open(filename) as df:
        try:
            logging.info(f'Parsing csv file: {df.name}')
            reader = csv.DictReader(df, delimiter=';')
        except Exception as e:
            logging.error(f'Failed to load csv file: {e}')

        try: 
            for row in reader:
                runMutation(row['App ID'],row['Relation ID'],row['ITComponent ID'],row['Attribute Value'], access_token)
        except Exception as e:
            logging.error(f'Error while processing factsheets: {e}')


# For updating an Attribute on relationship, you will need RelationshipID along with the FactSheetID and the targetFactSheet ID which we exported in exportRelationships.py
def runMutation(factSheetId,relationId,targetId,attributeValue, access_token):
    """Runs the mutation to alter an attribute on a relation.

    Args:
        factSheetId (str): ID of factsheet.
        relationId (str): ID of the relation
        targetId (str): ID of the target of the relation.
        attributeValue (str): Value of the attribute on the relation.
        access_token (str): Access token.
    """    
    attribute = "technicalSuitability"
    path = "/relApplicationToITComponent/"+relationId
    logging.info(attributeValue)
    patches = "{op: replace, path: \""+path+"\", value: \"{\\\""+attribute+"\\\": \\\""+attributeValue+"\\\",\\\"factSheetId\\\": \\\""+ targetId +"\\\"}\"}"
    query = """
    mutation{
        updateFactSheet(id: "%s",patches: [%s]) {
        factSheet {
        id
        name
        }
        }
      }
    """ % (factSheetId, patches)
    response_mutation = call("query", query, access_token)
    logging.info(response_mutation)

# General function to call GraphQL given a query
def call(request_type, query, access_token):
    """Posts the request to GraphQL.

    Args:
        request_type (str): Type of the query.
        query (dict): The query itself.
        access_token (str): Access token.

    Returns:
        _type_: _description_
    """    
    auth_header = f'Bearer {access_token}'
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