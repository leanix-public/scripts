import json 
import requests 
import pandas as pd
import base64
import time

## In order to run this script, an extra file called "access.json" needs to be added to the same folder. Content should look like this:
# {"api-token":"<your api-token>"}

api_token = None
#Alternatively, the api_token could be passed in the python script itself. In order to do this, uncomment the following line
#api_token = "<your api-token>"
auth_url = 'https://svc.leanix.net/services/mtm/v1/oauth2/token' 
mtm_base_url = 'https://svc.leanix.net/services/mtm/v1' 
pathfinder_base_url = 'https://app.leanix.net/services/pathfinder/v1'

def getApiToken():
  global api_token
  if api_token == None:
    with open('access.json') as json_file:  
      data = json.load(json_file)
      api_token = data['apitoken']
  return api_token
  
def getAccessToken(api_token):
  #different than callPost since it needs to send the auth_header
  response = requests.post(auth_url, auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'})
  response.raise_for_status() 
  access_token = response.json()['access_token']
  return access_token

def getHeader(access_token):
  return {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}

# Function to decipher the access_token
def getAccessTokenJson(access_token):
  payload_part = access_token.split('.')[1]
  # fix missing padding for this base64 encoded string.
  # If number of bytes is not dividable by 4, append '=' until it is.
  missing_padding = len(payload_part) % 4
  if missing_padding != 0:
    payload_part += '='* (4 - missing_padding)
  payload = json.loads(base64.b64decode(payload_part))
  return payload

def getInstanceUrl(access_token):
  access_token_json = getAccessTokenJson(access_token)
  return int(access_token_json["instanceUrl"])

def getExpiryTime(access_token):
  access_token_json = getAccessTokenJson(access_token)
  return int(access_token_json["exp"])

def getWorkspaceId(access_token):
  access_token_json = getAccessTokenJson(access_token)
  return access_token_json['principal']['permission']['workspaceId']

def getWorkspaceName(access_token):
  access_token_json = getAccessTokenJson(access_token)
  return access_token_json['principal']['permission']['workspaceName']

# General function to call a get API-Point 
def callGet(request_url, header):
  response = requests.get(url=request_url, headers=header)
  response.raise_for_status()
  return response.json()

# General function to call a post API-Point 
def callPost(request_url, header, data):
  try:
    response = requests.post(url=request_url, headers=header, data=json.dumps(data))
    response.raise_for_status()
  except requests.exceptions.HTTPError as err:
    print(request_url)
    print(json.dumps(data))
    print(err)
    exit
  return response.json()

## Here it is possible to paste the prepared GraphQL from GraphiQL
def getGraphQlQuery():
  query = """{
  allFactSheets(filter: {facetFilters: [
    {facetKey:"Subscriptions", operator:NOR, keys:["__missing__"]}
    #,{facetKey: "FactSheetTypes", keys: ["Application"]},
    #The second filter is used to filter out all applications without related ITComponents
    #,{facetKey:"relApplicationToITComponent", operator: NOR, keys:["__missing__"]}
      ]}) {
      totalCount
    edges {
      node {
        id
        type
        name
        description        
#        ... on Application {
#          lifecycle{phases{phase startDate}}         
#        }
        subscriptions{
          edges{
            node{
              id
              user{
                id 
                userName
                permission{
                  status
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
  return {"query": query}

def getGraphQl(query, access_token):
  response = callPost(pathfinder_base_url+'/graphql', getHeader(access_token), query)
  return response

access_token = getAccessToken(getApiToken())

print(json.dumps(getGraphQl(getGraphQlQuery(),access_token),indent=2,sort_keys=True))