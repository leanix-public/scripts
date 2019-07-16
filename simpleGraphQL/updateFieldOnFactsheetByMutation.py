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

## This function allows us to filter and retrieve all the Factsheets that we would like to update.
def getGraphQlQuery():
  query = """  {allFactSheets(filter: {facetFilters: [
    {facetKey: "FactSheetTypes", keys: ["Application"]},
    # Additional filters can be added here.
    # The second filter provides an example to filter out all applications without related ITComponents
    #,{facetKey:"relApplicationToITComponent", operator: NOR, keys:["__missing__"]}
      ]}) {
      totalCount
    edges {
      node {
        id
        rev
        ...on Application{
          legalAssessmentId
          legalApprovalComment
        }
      }
    }
  }
  }
  """
  return {"query": query}

## This function basically contains the graphQL query which can be pulled from the Browser Developer Tools.
## The %s and %d contains ways of adding string and number variables to the predefined query
def prepMutation(id,rev,assessmentId,assessmentComment):
  query = {
      "query": """mutation($patches:[Patch]!){result:updateFactSheet(id:\"%s\", rev:%d, patches:$patches, validateOnly:false){factSheet{id}}}""",
      "variables": {
          "patches": [
              {
                  "op": "replace",
                  "path": "/linkToLegalAssessmentId",
                  "value": "{\"externalId\":\"%s\"}"%(assessmentId)
              },
              {
                  "op": "replace",
                  "path": "/linkToLegalApprovalComment",
                  "value": "{\"externalId\":\"%s\",\"comment\":null}"%(assessmentComment)
              }
          ]
      }
  }
  return query


def getGraphQl(query, access_token):
  response = callPost(pathfinder_base_url+'/graphql', getHeader(access_token), query)
  return response

access_token = getAccessToken(getApiToken())

data = getGraphQl(getGraphQlQuery(),access_token)

for fs in data['data']['allFactSheets']['edges']:
  result = getGraphQl(prepMutation(fs['node']['id'],fs['node']['rev'],fs['node']['legalAssessmentId'],fs['node']['legalApprovalComment']),access_token)
  if result['data']['result'] is None :
    print(json.dumps(result['errors'])) 