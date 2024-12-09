# -*- coding: utf-8 -*-
"""Script for changing bookmark owner.

This script allows the user to change the owner of a bookmark.
Changes are indicated in a given input file.

Example:
    $ LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> python changeBookmarkOwner.py

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
import logging
import os


logging.basicConfig(level=logging.INFO)

#Request timeout
TIMEOUT = 20

#API token and subdomain set as env variables
LEANIX_API_TOKEN = os.getenv('LEANIX_API_TOKEN')
LEANIX_SUBDOMAIN = os.getenv('LEANIX_SUBDOMAIN')

LEANIX_AUTH_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net/services/mtm/v1/oauth2/token' 
LEANIX_REQUEST_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net/services/pathfinder/v1/bookmarks'


# this file updates the owner to the support user to be able to update write-restricted bookmarks too and saves the old owner

# api token, SVC instance and request URL
auth_url = LEANIX_AUTH_URL
request_url = LEANIX_REQUEST_URL

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


# function to get a bookmark by referencing its ID
def getBookmark(bookmarkId, header):
    """Retrieve a bookmark indicated by its ID.

    Args:
        bookmarkId (str): ID of the bookmark.
        header (dict): Authorization header.

    Returns:
        json: Response of the query.
    """    
    response = requests.get(url=request_url+"/"+bookmarkId, headers=header, timeout=TIMEOUT)
    return response.json()

# function to update bookmark
def updateBookmark(id, data, header):
    """Updates a bookmark with the given data.

    Args:
        id (str): _description_
        data (str): Data with the wanted updates to the bookmark.
        header (dict): Authorization header.

    Returns:
        json: Response of the query.
    """    
    response = requests.put(url=request_url+"/"+id, headers=header, data=data, timeout=TIMEOUT)
    return response.json()


# get bookmark and owner IDs from CSV
try:
    header = get_bearer_token(LEANIX_AUTH_URL, LEANIX_API_TOKEN)
except Exception as e:
    logging.error(f'Error while authenticating: {e}')

with open('bookmarkUpdates.csv') as df:
    try:
        logging.info(f'Parsing csv file: {df.name}')
        reader = csv.DictReader(df, delimiter=';')
    except Exception as e:
        logging.error(f'Failed to load csv file: {e}')

# main code
oldOwners = []

for bookmarkUpdate in reader:

    workspaceBookmark = getBookmark(bookmarkUpdate["id"], header)

    ownerIds = [bookmarkUpdate["id"], bookmarkUpdate["userId"]]
    oldOwners.append(ownerIds)

    workspaceBookmark["data"]["userId"] = bookmarkUpdate["userId"]

    payload = json.dumps(workspaceBookmark["data"])

    response = updateBookmark(bookmarkUpdate["id"], payload, header)
    logging.info("Owner changed for bookmark id:", bookmarkUpdate["id"])

# save old bookmark owners
oldOwnersFile = json.dumps(oldOwners, indent=2)

with open('oldBookmarkOwners.txt', 'w') as file:
    file.write(oldOwnersFile)