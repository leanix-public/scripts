import json 
import requests 
import pandas as pd
import base64
import time

mtm_base_url = 'https://svc.leanix.net/services/mtm/v1' 
pathfinder_base_url = 'https://app.leanix.net/services/pathfinder/v1'

def getAccessToken(api_token):
  #different than callPost since it needs to send the auth_header
  response = requests.post(mtm_base_url+"/oauth2/token", auth=('apitoken', api_token),
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


def getExpiryTime(access_token_json):
  return int(access_token_json["exp"])

def getWorkspaceId(access_token_json):
  return access_token_json['principal']['permission']['workspaceId']

def getWorkspaceName(access_token, workspaceId):
  response = callGet(mtm_base_url + '/workspaces/' + workspaceId, getHeader(access_token))
  return response['data']['name']

# General function to call GraphQL given a query
def callGet(request_url, header):
  response = requests.get(url=request_url, headers=header)
  response.raise_for_status()
  return response.json()

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

def getApiToken():
  with open('../access.json') as json_file:  
    data = json.load(json_file)
    return data['apitoken']

def getAllFactsheetsQuery():
  query = """
  {
    allFactSheets {
      edges {
        node {
          name
          id
          type
        }
      }
    }
  }
  """
  return {"query": query}

def getGraphQl(query, access_token):
  response = callPost(pathfinder_base_url+'/graphql', getHeader(access_token), query)
  return response

# in case the script lasts longer than the expiry time 
# and the access_token needs refreshing
def testAccessTokenExpiry(access_token_json):
  if (getExpiryTime(access_token_json) - time.mktime(time.localtime())) > 5:
    return True
  return False

def getUserCreate(fsId):
  query = """
  query allFactSheetCreates{
    allLogEvents(factSheetId:"%s", eventTypes:[FACT_SHEET_CREATED]){
      edges{
        node{
          user{
            userName
            email
            id 
          }
        }
      }
    }
  }"""%(fsId)
  return {"query":query}

access_token = getAccessToken(getApiToken())
access_token_json = getAccessTokenJson(access_token)
