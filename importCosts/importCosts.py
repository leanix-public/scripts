# -*- coding: utf-8 -*-
"""Script for importing costs.

This script allows the user to import costs.
The costs are indicated in the import file.

Example:
    $ LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> IMPORT_FILE=<your input file> python importCosts.py

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


# Function to create an application via GraphQL
def createApplication(name, header):
  """Creates an application under the given name.

  Args:
      name (str): Name of the application.
      header (dict): Authorization header.

  Returns:
      str: ID of the application
  """  
  query = """
    mutation {
    createFactSheet(input: {name: "%s", type: Application}) {
      factSheet {
        id
      }
    }
  }
  """ % (name)
  logging.info("Create Application " + name)
  response = call(query, header, LEANIX_REQUEST_URL)
  return response['data']['createFactSheet']['factSheet']['id'] 


# Function to create an IT Component via GraphQL
def createITComponent(name, header):
  """Creates an it component under the given name.

  Args:
      name (str): Name of the it component.
      header (dict): Authorization header.

  Returns:
      str: ID of the it component.
  """  
  query = """
    mutation {
    createFactSheet(input: {name: "%s", type: ITComponent}) {
      factSheet {
        id
      }
    }
  }
  """ % (name)
  logging.info("Create IT Component " + name)
  response = call(query, header, LEANIX_REQUEST_URL)
  return response['data']['createFactSheet']['factSheet']['id'] 


# Function to create a relation between Application and IT Component with the costs attribute
def createRelationWithCosts(app, itc, costs, header) :
  """Creates a relation with the created factsheets and the given cost.

  Args:
      app (str): ID of the application.
      itc (str):  ID of the it component.
      costs (str): Costs of the relation between the prior factsheets.
      header (dict): Authorization header.
  """  
  query = """
    mutation {
      updateFactSheet(id: "%s", 
                      patches: [{op: add, path: "/relITComponentToApplication/new_1", value: "{\\\"factSheetId\\\": \\\"%s\\\",\\\"costTotalAnnual\\\": %s}"}]) {
        factSheet {
          id
        } 
      }
    }
  """ % (itc, app, costs)
  logging.info("Create relation with costs: " + itc + "->" + app + " = " + str(costs))
  call(query, header, LEANIX_REQUEST_URL)


# Start of the main logic
try:
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, IMPORT_FILE)
except ValueError:
    logging.error('Failed to parse file input')

# 1. Read the input as a CSV
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

    data = [row for row in reader]

    # 2. Make sure to create all applications, and save the created ids
    try:
      apps = {}

      appNames = set(row['app'] for row in data)
      for appName in appNames:
        apps[appName] = createApplication(appName, header)
        logging.info(apps[appName])
    except Exception as e:
      logging.error(f'Failed to create applications: {e}')
    
    # 3. Make sure to create all IT Components, and save the created ids
    try:
      itcs = {}

      itc_values = set(row['itc'] for row in data)
      for itc_value in itc_values:
        itcs[itc_value] = createITComponent(itc_value, header)
        logging.info(itcs[itc_value])
    except Exception as e:
      logging.error(f'Failed to create it components: {e}')
    
    # 4. Create the relations based on the saved ids
    try:
      for row in data:
        createRelationWithCosts(apps[row['app']], itcs[row['itc']], row['costs'], header)
    except Exception as e:
      logging.error(f'Failed to create relations: {e}')