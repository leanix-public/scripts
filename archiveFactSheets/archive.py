# -*- coding: utf-8 -*-
"""Script for archiving the specified factsheets in an input file.

This script allows the user to archive factsheets from their workspace.
The factsheets specified in the given input file will be set to ARCHIVED
upon successful completion of the script. This script also uses cli inputs
to gather all the necessary information.

Example:
    $ LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> IMPORT_FILE=<your input file> python archiveFactsheets.py

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
    auth_header = f'Bearer {access_token}'
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


# Delete the subscription
def archiveFactSheets(id, header):
    """Function to construct the query for archiving a certain factsheet.

    Args:
        id (str): ID for the factsheets that is to be archived.
    """  
    query = """
    mutation {
      updateFactSheet(id: "%s", comment: "Archive", patches: {op: replace, path: \"/status\", value: \"ARCHIVED\"}, validateOnly: false) {
        factSheet {
          id
        }
      }
    }
    """ % (id)
    logging.info(f'Archiving fact sheet with id: {id}')
    response = call(query, header, LEANIX_REQUEST_URL)
    logging.debug(response)


# Start of the main program
def main ():
    
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


        try: 
            for row in reader:
                archiveFactSheets(row['id'], header)

        except Exception as e:
            logging.error(f'Error while processing factsheets: {e}')


if __name__ == "__main__":
    main()
