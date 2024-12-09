# -*- coding: utf-8 -*-
"""Script for populating the aces on a factsheet based on set relations to user groups.

This script allows the user to automatie the ace population on viable factsheets. The aces are
set based on present relations to user groups.

Example:
    $ LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> IMPORT_FILE=<your input file> python populateaces.py

Global variables:
    TIMEOUT (int): Timeout for requests.
    LEANIX_API_TOKEN (str): API-Token to authenticate with.
    LEANIX_SUBDOMAIN (str): LeanIX subdomain.
    LEANIX_BASE_URL (str): The base of every url.
    LEANIX_AUTH_URL (str): URL to authenticate against.
    request_url (str): URL to send graphql requests to.

"""

import requests
import json
import re
import os


LEANIX_API_TOKEN = os.getenv('LEANIX_API_TOKEN')
LEANIX_SUBDOMAIN = os.getenv('LEANIX_SUBDOMAIN')

LEANIX_BASE_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net' 
LEANIX_AUTH_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net/services/mtm/v1/oauth2/token' 
request_url = f"https://{LEANIX_SUBDOMAIN}.leanix.net/services/pathfinder/v1/graphql" 
TIMEOUT = 20


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

def call(data, header):
  json_data = json.dumps(data)
  response = requests.post(url=request_url, headers=header, data=json_data)
  response.raise_for_status()
  return response.json()

# Remmove an existing ACE from a factsheet
def removeAllACE(fsId, header):
    """Removes all ACEs on a factsheet.

    Args:
        fsId (str): The id of the factsheet that is looked at.
        header (dict): The authorization header used in the graphql query.

    Returns:
        dict: The response of the query.
    """    
    query = """
        mutation {
            updateFactSheet(
                id: "%s",
                    patches: [{op: replace, path: \"/permittedReadACL\", value: \"[]\" },
                             {op: replace, path: \"/permittedWriteACL\", value: \"[]\" }]
                ) {
                    factSheet {
                        id
                        displayName
                    }
                }
        }
    """%(fsId)
    
    data = {"query" : query}
    response = call(data, header)
    return response

# Query relations
def getRelations(fsId, header):
    """Query all relations to UserGroups of a given factsheet.

    Args:
        fsId (str): The id of the factsheet that is looked at.
        header (dict): The authorization header used in the graphql query.

    Returns:
        dict: Dictionary containing all relations present in a factsheet.
    """    
    graphql_query = """{
                        factSheet(id: "%s") {
                            ... on UserGroup {
                                id
                                name
                                relUserGroupToApplication {
                                    edges {
                                        node {
                                            factSheet {
                                                id
                                                displayName
                                                type
                                            }
                                        }
                                    }
                                }
                                relUserGroupToITComponent {
                                    edges {
                                        node {
                                            factSheet {
                                                id
                                                displayName
                                                type
                                            }
                                        }
                                    }
                                }
                                relUserGroupToProject {
                                    edges {
                                        node {
                                            factSheet {
                                                id
                                                displayName
                                                type
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }"""%(fsId)
    data = {"query" : graphql_query}

    response = call(data, header)
    return response


# Decodes the set relations and determines the name of the related user group 
def retrieveUserGroupRelationsByFSType(relations):
    """This function sorts all relations based on their type.

    Args:
        relations (dict): All relations set on a factsheet.

    Returns:
        dict: All relations sorted by type.
    """    
    relToApplications = []
    for rel in relations["data"]["factSheet"]["relUserGroupToApplication"]["edges"]:
        if rel["node"]["factSheet"]["type"] == "Application":
            relToApplications.append(rel["node"]["factSheet"]["id"])

    relToITComponents = []
    for rel in relations["data"]["factSheet"]["relUserGroupToITComponent"]["edges"]:
        if rel["node"]["factSheet"]["type"] == "ITComponent":
            relToITComponents.append(rel["node"]["factSheet"]["id"])

    relToProjects = []
    for rel in relations["data"]["factSheet"]["relUserGroupToProject"]["edges"]:
        if rel["node"]["factSheet"]["type"] == "Project":
            relToProjects.append(rel["node"]["factSheet"]["id"])

    allRelations = {
        "relToApplications" : relToApplications,
        "relToITComponents" : relToITComponents,
        "relToProjects" : relToProjects 
    }

    return allRelations


def getAllACEs(header, url):
    """Gets all ACEs set in a workspace.

    Args:
        header (dict): The authorization header used in the graphql query.
        url (str): The base-URL to send the request to.

    Returns:
        dict: A dictionary containing all ACEs in a given workspace.
    """    
    response = requests.get(url=url + "/services/pathfinder/v1/models/accessControlEntities?pageSize=40&sorting=name&sortDirection=ASC", headers=header)
    response.raise_for_status()
    return response.json()


# Add an ACE to a factsheet
def addACE(fsId, header, idsRead, idsWrite):
    """Adds an ACE to the given factsheet.

    Args:
        fsId (str): The id of the factsheet that is looked at.
        header (dict): The authorization header used in the graphql query.
        idsRead (list): List of read ACE-ids
        idsWrite (list): List of write ACE-ids

    Returns:
        dict: The response of the executed mutation.
    """    
    patchRead = ""
    for ir in idsRead:
        patchRead += "{\\\"id\\\":\\\"%s\\\"},"%(ir)
    patchRead = patchRead.rstrip(",")
    
    patchWrite = ""
    for iw in idsWrite:
        patchWrite += "{\\\"id\\\":\\\"%s\\\"},"%(iw)
    patchWrite = patchWrite.rstrip(",")
    
    query = """
        mutation {
            updateFactSheet(
                id: "%s",
                    patches: [{op: replace, path: \"/permittedReadACL\", value: \"[%s]\" },
                             {op: replace, path: \"/permittedWriteACL\", value: \"[%s]\" }]
                ) {
                    factSheet {
                        id
                        displayName
                    }
                }
        }
    """%(fsId, patchRead, patchWrite)
    
    data = {"query" : query}
    response = call(data, header)
    return response


# Get the set user groups of a given factsheet
def getUserGroups(fsId, header):
    """Gets the UserGroups a given factsheet points to.

    Args:
        fsId (str): The id of the factsheet that is looked at.
        header (dict): The authorization header used in the graphql query.

    Returns:
        dict: All UserGroups the factsheet points to.
    """    
    graphql_query = """{
                        factSheet(id: "%s") {
                            ... on Application {
                                id
                                name
                                relApplicationToUserGroup {
                                    edges {
                                        node {
                                            factSheet {
                                                displayName
                                                id
                                            }
                                        }
                                    }
                                }
                            }
                            ... on ITComponent {
                                id
                                name
                                relITComponentToUserGroup {
                                    edges {
                                        node {
                                            factSheet {
                                                displayName
                                                id
                                            }
                                        }
                                    }
                                }
                            }
                            ... on Project {
                                id
                                name
                                relProjectToUserGroup {
                                    edges {
                                        node {
                                            factSheet {
                                                displayName
                                                id
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }"""%(fsId)
    data = {"query" : graphql_query}

    response = call(data, header)
    return response


# Function to get the ID of an ACE based on a given name
def getACEId(acename, allaces, header):
    """Retrieves the id of an ACE based on a given name.

    Args:
        acename (str): The name of the ACE.
        allaces (dict): All ACEs present in a workspace.
        header (dict): The authorization header used in the graphql query.

    Returns:
        str: The if of the ACE found.
    """    
    for entity in allaces["data"]:
        if entity["displayName"] == acename:
            return entity["id"]

    return ""


# Creates an ACE based on the given data
def createACE(header, id, name, description, url):
    """Creates an ACE in the given workspace with the provided id, name and description.

    Args:
        header (dict): The authorization header used in the graphql query.
        id (str): The id of the ACE.
        name (str): The name of the ACE.
        description (str): The description of the ACE.
        url (str): The base-URL to send the request to.

    Returns:
        dict: Response of the request.
    """    
    header["Content-Type"] = "application/json"
    json_data = {
        "name": id,
        "displayName": name,
        "description": description
    }
    response = requests.post(url=url + "/services/pathfinder/v1/models/accessControlEntities", headers=header, data=json.dumps(json_data))
    return response.json()


# Get all user groups present in a workspace
def getAllUserGroups(header):
    """This function queries all factsheets of the type "UserGroup" and their ids.

    Args:
        header (dict): The authorization header used in the graphql query.

    Returns:
        dict: The response of the query containing all UserGroup factsheets.
    """ 
    graphql_query = """{
                        allFactSheets(factSheetType: UserGroup) {
                            edges {
                                node {
                                    displayName
                                    id
                                }
                            }
                        }
                    }"""
    data = {"query" : graphql_query}

    response = call(data, header)
    return response


header = get_bearer_token(LEANIX_AUTH_URL, LEANIX_API_TOKEN)

# Retrieves all usergroups in a given workspace
allUserGroups = getAllUserGroups(header)
# Iterate through every usergroup
for usergroupid in allUserGroups["data"]["allFactSheets"]["edges"]:
    tmpdict = retrieveUserGroupRelationsByFSType(getRelations(usergroupid["node"]["id"], header))
    allids = []
    # Puts together a list of all factsheets that have a relation set to the currently worked on usergroup
    for id in tmpdict["relToApplications"]:
        allids.append(id)
    for id in tmpdict["relToITComponents"]:
        allids.append(id)
    for id in tmpdict["relToProjects"]:
        allids.append(id)
    for factsId in allids:
        tmpgroups= getUserGroups(factsId, header)
        print(tmpgroups)

        # Create a list of all usergroup names a factsheets has set
        usergroupnames = []
        for key, value in tmpgroups["data"]["factSheet"].items():
            if key.endswith("ToUserGroup"):
                for group in value["edges"]:
                    usergroupnames.append(group["node"]["factSheet"]["displayName"])

        # Query all set ACEs
        aces = getAllACEs(header, LEANIX_BASE_URL)

        # Create a list of the ids of the ACEs
        aceIdList = []
        for usergroup in usergroupnames:
            usergroup = re.sub(r' \(recovered.*$', '', usergroup) # Strips the ...(recovered...) part, in case of a recovery of a factsheet
            aceid = getACEId(usergroup, aces, header)
            if aceid:
                aceIdList.append(getACEId(usergroup, aces, header))
            else:
                # In case no ACE is present for a usergroup, create a new one
                name = usergroup
                newACEId = ''.join(name.split()).lower()
                description = "Test desc" # Placeholder! Change to the correct description
                aceIdList.append(createACE(header, newACEId, name, description, LEANIX_BASE_URL)["data"]["id"])

        # Removing all previous set ACEs of a given factsheet
        response = removeAllACE(factsId, header)

        # Create ACEs based on the previously retrieved ids
        if aceIdList:
            response = addACE(factsId, header, aceIdList, aceIdList)

        print(response)
