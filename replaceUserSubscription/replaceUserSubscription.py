# -*- coding: utf-8 -*-
"""Script for replacing user subscriptions.

This script allows the user to replace user subscriptions.
The old and new users are indicated in the global variables.

Example:
    $ LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> NEW_USER=<> OLD_USER=<> python replaceUserSubscription.py

Global variables:
    TIMEOUT (int): Timeout for requests.
    LEANIX_API_TOKEN (str): API-Token to authenticate with.
    LEANIX_SUBDOMAIN (str): LeanIX subdomain.
    LEANIX_AUTH_URL (str): URL to authenticate against.
    LEANIX_REQUEST_URL (str): URL to send graphql requests to.
    NEW_USER (str): E-Mail of the new user.
    OLD_USER (str): E-Mail of the old user.

"""

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

NEW_USER = os.getenv('NEW_USER')
OLD_USER = os.getenv('OLD_USER')


#INPUT
auth_url = LEANIX_AUTH_URL
request_url = LEANIX_REQUEST_URL

api_token = LEANIX_API_TOKEN

oldUser = OLD_USER
newUser = NEW_USER


# Get the bearer token - see https://dev.leanix.net/v4.0/docs/authentication
response = requests.post(auth_url, auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'})
response.raise_for_status() 
access_token = response.json()['access_token']
auth_header = f'Bearer {access_token}'
header = {'Authorization': auth_header}

# General function to call GraphQL given a query
def call(query):
  """Function to post a request to GraphQL.

  Args:
      query (str): The query you want to run.

  Returns:
      str: Response of the query.
  """  
  data = {"query" : query}
  json_data = json.dumps(data)
  response = requests.post(url=request_url, headers=header, data=json_data, timeout=TIMEOUT)
  response.raise_for_status()
  return response.json()


def getSubscriptionPage(endCursor):
  query = """
  {
    allFactSheets(first: 10000, after: "%s") {
      pageInfo {
        hasNextPage
        endCursor
      }
      edges {
        node {
          id
          subscriptions {
            edges {
              node {
                id
                user {
                  email
                }
                type
                roles {
                  id
                  comment
                }
              }
            }
          }
        }
      }
    }
  } 
  """ % (endCursor)
  response = call(query)
  return response

def extractSubscriptions(response,user):
  subscriptions = []
  for fs in response['data']['allFactSheets']['edges']:
    for subscription in fs['node']['subscriptions']['edges']:
      if subscription['node']['user']['email'] == user:
        subscriptions.append({'id': subscription['node']['id'], 'fsId': fs['node']['id'], 'type': subscription['node']['type']})
  return subscriptions

def getAllSubscriptions(user):
  subscriptions = []
  first = getSubscriptionPage("")
  subscriptions.append(extractSubscriptions(first,user))
  while first['data']['allFactSheets']['pageInfo']['hasNextPage']:
    endCursor = first['data']['allFactSheets']['pageInfo']['endCursor']
    first = getSubscriptionPage(endCursor)
    subscriptions.append(extractSubscriptions(first,user))
  return subscriptions

def getRoles(fsId, user):
  query = """
  {
    factSheet(id: "%s") {
      id
      subscriptions {
        edges {
          node {
            user {
              email
            }
            roles {
              id
              comment
            }
          }
        }
      }
    }
  }
  """ % (fsId)
  response = call(query)
  for subscription in response['data']['factSheet']['subscriptions']['edges']:
    if subscription['node']['user']['email'] == user:
      return subscription['node']['roles']
  return []

def createSubscription(fsId, user, type, roles) :
  query = """
    mutation {
      createSubscription(factSheetId: "%s", user: {email: "%s"}, type: %s, roles: [%s]) {
        id
    }
  }
  """ % (fsId, user, type, roles)
  logging.info("Create new subscription for: " + fsId)
  response = call(query)
  logging.debug(response)

def deleteSubscription(id, fsId) :
  query = """
    mutation {
      deleteSubscription(id: "%s") {
        id
    }
  }
  """ % (id)
  logging.info("Delete old subscription for: " + fsId)
  response = call(query)
  logging.debug(response)

def updateSubscription(subscription, oldUser, newUser):
  roles = []
  for role in getRoles(subscription['fsId'], oldUser):
    roles.append("{id: \"" + role['id'] + "\", comment: \"" + (role['comment'] if role['comment'] is not None else "") + "\"}")
  createSubscription(subscription['fsId'], newUser, subscription['type'],  ",".join(roles))

  deleteSubscription(subscription['id'], subscription['fsId'])

# Start of the main program
#oldUser = 'srv.FrancoisKrugerDemo@meshlab.de'
#newUser = 'cio.FrancoisKrugerDemo@meshlab.de'

for subscription in getAllSubscriptions(oldUser):
  if isinstance(subscription, list):
    for subscr in subscription:
      updateSubscription(subscr, oldUser, newUser)
  else:
    updateSubscription(subscription, oldUser, newUser) 

