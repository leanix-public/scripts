# -*- coding: utf-8 -*-
"""Script for breaking quality seals.

This script allows the user to break quality seals.
It queries all factsheets of the given type and breaks their quality seal.

Example:
    $ LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> FACTSHEET_TYPE=<> python breakQualitySeal.py

Global variables:
    TIMEOUT (int): Timeout for requests.
    LEANIX_API_TOKEN (str): API-Token to authenticate with.
    LEANIX_SUBDOMAIN (str): LeanIX subdomain.
    LEANIX_AUTH_URL (str): URL to authenticate against.
    LEANIX_REQUEST_URL (str): URL to send graphql requests to.

"""

import json 
import requests 
import os
import logging

# In order to break the quality seal we do not have a direct query. Hence the option available is to use a specific field
# on a FactSheet and update it using a member.
# 1. Set the api_token in line 10 of a Technical user who has MEMBER role
# 2. Modify the request_url as per your instance i.e. customer.leanix.net
# 3. Modify the factSheetType in order to update all the FactSheets, if you want to update the specific FactSheets adjust the query in getAllApps()
# 4. Modify the field to be updated as per the requirement in updateFactSheet()
#

logging.basicConfig(level=logging.INFO)

#Request timeout
TIMEOUT = 20

#API token and subdomain set as env variables
LEANIX_API_TOKEN = os.getenv('LEANIX_API_TOKEN')
LEANIX_SUBDOMAIN = os.getenv('LEANIX_SUBDOMAIN')

LEANIX_AUTH_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net/services/mtm/v1/oauth2/token' 
LEANIX_REQUEST_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net/services/pathfinder/v1/graphql'

FACTSHEET_TYPE = os.getenv('FACTSHEET_TYPE')


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


# Read all existing FactSheets as per factSheetType - Modify this to break the quality Seal as per requirement.
def getAllApps(factSheetType, header):
  """Retrieves all applications.

  Args:
      factSheetType (str): Type of the factsheet you want to query.
      header (dict): Authorization header.

  Returns:
      list: List of all applications.
  """  
  query = """
  {
    allFactSheets(factSheetType: %s) {
      edges {
        node {
          id
        }
      }
    }
  }
  """ % (factSheetType)
  response = call(query, header, LEANIX_REQUEST_URL)
  apps = []
  for appNode in response['data']['allFactSheets']['edges']:
    appId = appNode['node']['id']
    apps.append(appId)
  return apps

def updateFactSheet(app, header) :
  #Here we are updating a field alias , but Ideal will be to create a new field for this purpose and update the field  
  """Function to update all factsheets.

  Args:
      app (str): IF of the application.
      header (dict): Authorization header.
  """  
  query = """
    mutation {
      updateFactSheet(id: "%s", 
                      patches: [{op: add, path: "/alias", value: "xx"}]) {
        factSheet {
          id
        } 
      }
    }
  """ % (app)
  response = call(query, header, LEANIX_REQUEST_URL)
  logging.debug(response)

# Start of the main program
try:
    header = get_bearer_token(LEANIX_AUTH_URL, LEANIX_API_TOKEN)
except Exception as e:
    logging.error(f'Error while authenticating: {e}')

# 1. Get the existing factsheets from LeanIX
try:
  apps = getAllApps(FACTSHEET_TYPE, header)
except Exception as e:
  logging.error(f'Error while retrieving all factsheets: {e}')

# 2. Update the quality sealfor each row
try:
  for app in apps:
    updateFactSheet(app, header)
except Exception as e:
  logging.error(f'Error while updating all factsheets: {e}')
