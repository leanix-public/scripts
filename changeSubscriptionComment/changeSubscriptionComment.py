# -*- coding: utf-8 -*-
import json 
import requests 
import os
import logging
import json

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


def getAllSubscriptionRoles(header):
    """Retrieve all subscription roles.

    Args:
        header (dict): Authorization header.

    Returns:
       str: Respones of the query.
    """    
    query = """
    query MyQuery {
        allSubscriptionRoles {
            edges {
                node {
                    description
                    id
                    mandatoryForFactSheetTypes
                    name
                    subscriptionType
                    restrictToFactSheetTypes
                }
            }
        }
    }
    """
    response = call(query, header, LEANIX_REQUEST_URL)
    return response


def updateSubscription(id, type, role_id, role_comment, user_id, header):
    query = """
    mutation {
        updateSubscription(
            id: "%s"
            type: %s
            roles: [{id: "%s", comment: "%s"}]
            user: {id: "%s"}
        ) {
            id
            factSheet {
                name
            }
        }
    }
    """ % (id, type, role_id, role_comment, user_id)

    response = call(query, header, LEANIX_REQUEST_URL)
    logging.info(response)


def getAllSubscriptions(header):
    query = """
    query MyQuery {
      allFactSheets {
        edges {
          node {
            subscriptions {
              edges {
                node {
                  type
                  id
                  factSheet {
                    id
                  }
                  user {
                    id
                  }
                  roles {
                    id
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
    return response


# Start of the main program
def main ():
    
    try:
        header = get_bearer_token(LEANIX_AUTH_URL, LEANIX_API_TOKEN)
    except Exception as e:
        logging.error(f'Error while authenticating: {e}')


    allSubscriptionRoles = getAllSubscriptionRoles(header)
    allSubscriptions = getAllSubscriptions(header)

    # mappings from all import information
    """[
    {
        "type" : OBSERVER
        "id" : "129038j902d1830982901j809d12830d2"
        "factSheet" : {
            "id" : "adij9241opwdj9que20opjqdwu290jqopwd29u"
        }
        "role" : {
            "id" : "sadasdn08qnid0d8qdioq8d0"
            "description" : "Test Desc"
        }
        "user" : "sdijoasdi2jiqo3kjq2"
    },
    ...
    ]
    """

    subscriptionRoleIDToDescriptionID = {}
    subscriptions = []

    # get mapping from subscriptionrole to its description and id
    for role in allSubscriptionRoles["data"]["allSubscriptionRoles"]["edges"]:
        sub_role_id = role["node"]["id"]
        sub_desc = role["node"]["description"]
        
        tmpDict = {"id" : sub_role_id,
                  "description" : sub_desc}

        subscriptionRoleIDToDescriptionID[sub_role_id] = tmpDict


    for factsheet in allSubscriptions["data"]["allFactSheets"]["edges"]:
        for subscription in factsheet["node"]["subscriptions"]["edges"]:
            subscriptionDict = {}

            # retrieve every needed value
            sub_role = subscription["node"]["roles"]
            if sub_role:
                sub_id = subscription["node"]["id"]
                sub_type = subscription["node"]["type"]
                sub_fs_id = subscription["node"]["factSheet"]["id"]
                sub_role_id = subscription["node"]["roles"][0]["id"]
                sub_user_id = subscription["node"]["user"]["id"]

                subscriptionDict["type"] = sub_type
                subscriptionDict["id"] = sub_id
                factSheetDict = {"id" : sub_fs_id}
                subscriptionDict["factSheet"] = factSheetDict
                subscriptionDict["role"] = subscriptionRoleIDToDescriptionID[sub_role_id]
                subscriptionDict["user"] = sub_user_id

                subscriptions.append(subscriptionDict)


    for subscription in subscriptions:
        updateSubscription(subscription["id"], subscription["type"], subscription["role"]["id"], subscription["role"]["description"], subscription["user"], header)


if __name__ == "__main__":
    main()
