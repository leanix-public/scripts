# -*- coding: utf-8 -*-
"""Script for exporting costs.

This script allows the user to export the costs of applications and their itcomponents.

Example:
    $ LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> python exportCosts.py

Global variables:
    TIMEOUT (int): Timeout for requests.
    LEANIX_API_TOKEN (str): API-Token to authenticate with.
    LEANIX_SUBDOMAIN (str): LeanIX subdomain.
    LEANIX_AUTH_URL (str): URL to authenticate against.
    LEANIX_REQUEST_URL (str): URL to send graphql requests to.

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

# Read all existing Application - IT Component relations
def exportCosts(header):
    """Query to export every cost.

    Args:
        header (dict): Authorization header.
    """    
    query = """
    {
      allFactSheets(factSheetType: Application) {
        edges {
          node {
            id
            displayName
            ... on Application {
              relApplicationToITComponent {
                edges {
                  node {
                    id
                    costTotalAnnual
                    factSheet {
                      id
                      displayName
                    }
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

    with open('result.csv', 'w') as csvfile:
      writer = csv.writer(csvfile, delimiter=';')
      writer.writerow(['App ID', 'App Display Name', 'ITC ID', 'ITC Display Name', 'Total Annual Costs'])
    
      for appNode in response['data']['allFactSheets']['edges']:
        appId = appNode['node']['id']
        appName = appNode['node']['displayName']
        for relationNode in appNode['node']['relApplicationToITComponent']['edges']:
          costs = relationNode['node']['costTotalAnnual']
          itcId = relationNode['node']['factSheet']['id']
          itcName = relationNode['node']['factSheet']['displayName']     
          writer.writerow([appId, appName, itcId, itcName, costs])


try:
    header = get_bearer_token(LEANIX_AUTH_URL, LEANIX_API_TOKEN)
except Exception as e:
    logging.error(f'Error while authenticating: {e}')

try:
  exportCosts(header)
except Exception as e:
   logging.error(f'Error while exporting costs: {e}')
