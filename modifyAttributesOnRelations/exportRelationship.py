# This Script can be used to export the relationships between two FactSheets along with the attributes on the relation.
# In this example we are looking at Application to ITC Relationship and Attribute on Relationship : technicalSuitability or Technical Fit.
# This script will export the fields, Application,ITC, Application to ITC Relationship and also the attribute technicalSuitability
# Output of this script is a file : Info.csv can be used as an input in importRelationship.py after making the relvant changes.
# Changes required in the Script :-
# 1. Adapt mtm_base_url as per your instance. Eg. us-svc,eu-svc
# 2. Adapt pathfinder_base_url and apiToken
# 3. Modify the query in getRelationVariablesToExport and include the attributes as per requirement.
# 4. Also modify the CSV writer and newObject to include your attributes.

import json 
import requests 
import base64
import csv
import os
import logging


"""
# 1. Adapt mtm_base_url as per your instance. Eg. us-svc,eu-svc
mtm_base_url = 'https://eu-svc.leanix.net/services/mtm/v1'
# 2. Adapt pathfinder_base_url
pathfinder_base_url = 'https://demo-eu.leanix.net/services/pathfinder/v1'
apiToken = ""
"""


logging.basicConfig(level=logging.INFO)

#Request timeout
TIMEOUT = 20

#API token and subdomain set as env variables
LEANIX_API_TOKEN = os.getenv('LEANIX_API_TOKEN')
LEANIX_SUBDOMAIN = os.getenv('LEANIX_SUBDOMAIN')

LEANIX_AUTH_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net/services/mtm/v1' 
LEANIX_REQUEST_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net/services/pathfinder/v1'

IMPORT_FILE = os.getenv('IMPORT_FILE')


#INPUT
mtm_base_url = LEANIX_AUTH_URL
pathfinder_base_url = LEANIX_REQUEST_URL

apiToken = LEANIX_API_TOKEN

def getAccessToken(api_token):
  """Retrieves the access token.

  Args:
      api_token (str): API-Token.

  Returns:
      str: Access token.
  """  
  #different than callPost since it needs to send the auth_header
  response = requests.post(mtm_base_url+"/oauth2/token", auth=('apitoken', api_token),
                                        data={'grant_type': 'client_credentials'})
  response.raise_for_status() 
  access_token = response.json()['access_token']
  return access_token



def getHeader(access_token):
  """Decipher the access token to get the bearer token.

  Args:
      access_token (str): Access token.

  Returns:
      str: Bearer token.
  """  
  return {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}

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
    payload_part += '='* (4 - missing_padding)
  payload = json.loads(base64.b64decode(payload_part))
  return payload

def callPost(request_url, header, data):
  """Post request with given data.

  Args:
      request_url (str): Request url.
      header (str): Header.
      data (str): Data of the request.

  Returns:
      dict: Response of the request.
  """  
  try:
    response = requests.post(url=request_url, headers=header,  data=json.dumps(data))
    response.raise_for_status()
  except requests.exceptions.HTTPError as err:
    logging.info(request_url)
    logging.info(json.dumps(data))
    logging.info(err)
    exit
  return response.json()



def updateHost(host):
  global pathfinder_base_url
  pathfinder_base_url = 'https://%s/services/pathfinder/v1'%(host)

def getApiToken():
  with open('../access.json') as json_file:  
    data = json.load(json_file)
#    if (data["host"] is not None):
#      updateHost(data["host"])
    return data['apiTokenExportRelations']

def postGraphQl(query, access_token):
  """Posts a query to GraphQL.

  Args:
      query (str): Query to be run against GraphQL.
      access_token (str): Access token.

  Returns:
      str: Response of the request.
  """  
  response = callPost(pathfinder_base_url+'/graphql', getHeader(access_token), query)
  return response



def getRelationVariablesToExport():
  """Returns the query to retrieve variables to export.

  Returns:
      dict: Query.
  """  
  query = """
      {
      allFactSheets(factSheetType: Application){
        totalCount
        edges{
          node{
            id
            displayName
            tags{
              id
              name
            }
            ... on Application{
              relApplicationToITComponent{
                edges{
                  node{
                    id
                    factSheet{
                      displayName
                      id
                    }
                    technicalSuitability
                  }
                }
            }
          }
        }
      }

    }
    }

  """
  return {"query": query}

def getSingleFactsheet():
  """Returns the query to retrieve relations of a single factsheet.

  Returns:
      dict: Query.
  """  
  query = """{    
  factSheet(id:"28fe4aa2-6e46-41a1-a131-72afb3acf256") {
            id
            displayName
            ... on Application{
              relApplicationToUserGroup{
                edges{
                  node{
                    id
                    activeFrom
                    activeUntil
                  }
                }
              }
            }
          }
  }
  """
  return {"query": query}



def getGraphQl(query, access_token):
  """Post query to GraphQL.

  Args:
      query (dict): Query.
      access_token (str): Access token.

  Returns:
      str: Response of the query.
  """  
  response = callPost(pathfinder_base_url+'/graphql', getHeader(access_token), query)
  return response


access_token = getAccessToken(apiToken)
access_token_json = getAccessTokenJson(access_token)


## notice the Dictionary Call ['data'] at the end ofhe function call.
data = getGraphQl(getRelationVariablesToExport(), access_token)['data']

#print(json.dumps(data,indent=2))

with open('Info.csv', 'w') as csvfile:
  #writer = csv.writer(csvfile, delimiter=';') #For German Locale, we need another delimiter
  writer = csv.writer(csvfile, delimiter=';')
  writer.writerow(['Application','App ID', 'ITComponent', 'ITComponent ID','Relation ID', 'Tags','Attribute Value'])

  for fsnode in data['allFactSheets']['edges']:
    fs = fsnode['node']
    tags = fs['tags']
    tagCots = ''
    for tag in tags:
      if tag['name'] == 'COTS Package':
        tagCots = 'COTS Package'
      if tag['name'] == 'No COTS Package':
        tagCots = 'No COTS Package'
    for dateNode in fs['relApplicationToITComponent']['edges']:
      newObject = {
        "application":fs['displayName'],
        "appId":fs['id'],
        "relationId":dateNode['node']['id'],
        "itcName":dateNode['node']['factSheet']['displayName'],
        "itcId":dateNode['node']['factSheet']['id'],
        "attributeValue":dateNode['node']['technicalSuitability'],
        "tagCots":tagCots
      }
      writer.writerow([newObject['application'],newObject['appId'],newObject['itcName'],newObject['itcId'],newObject['relationId'],newObject['tagCots'],newObject['attributeValue']])