import json 
import requests 
import pandas as pd
import base64
import time


"""
api_token = ''
auth_url = 'https://abc.leanix.net/services/mtm/v1/oauth2/token' 
#request_url = 'https://svc.leanix.net/services/mtm/v1' 
mtm_base_url = 'https://svc.leanix.net/services/mtm/v1' 
pathfinder_base_url = 'https://demo-eu.leanix.net/services/pathfinder/v1'
"""


#INPUT
auth_url = "Placeholder"

api_token = input("Enter your API-Token: ")

print("")
print("Choose the instance your workspace is on:")
print("")
print("1. EU")
print("2. US")
print("3. AU")
print("4. UK")
print("5. DE")
print("6. CH")
print("7. AE")
print("8. CA")
print("9. BR")
print(" ")

try:
    choice = input("Enter your choice (1/2/3/4/5/6/7/8/9): ")
           
    if choice == "1":
        instance = "eu"
    elif choice == "2":
        instance = "us"
    elif choice == "3":
        instance = "au"
    elif choice == "4":
        instance = "uk"
    elif choice == "5":
        instance = "de"
    elif choice == "6":
        instance = "ch"
    elif choice == "7":
        instance = "ae"
    elif choice == "8":
        instance = "ca"
    elif choice == "9":
        instance = "br"
    elif choice == "10":
        instance = "eu"
    else:
        print("")
        print("Invalid choice. Please select 1, 2, 3, 4, 5, 6, 7, 8 or 9")
        print("")

except ValueError:
    print("")
    print("Invalid input. Please enter a number.")
    print("")

try:
    auth_url = 'https://' + instance + '-svc.leanix.net/services/mtm/v1/oauth2/token' 

    mtm_base_url = 'https://' + instance + '-svc.leanix.net/services/mtm/v1'

    if choice == "10":
        pathfinder_base_url = 'https://demo-' + instance + '-1.leanix.net/services/pathfinder/v1'
    else:
        pathfinder_base_url = 'https://' + instance + '.leanix.net/services/pathfinder/v1'

except NameError:
    print("")
    print("Invalid input. Please enter a number.")
    print("")
    exit()


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
  with open('access.json') as json_file:  
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

access_token = getAccessToken(api_token)
access_token_json = getAccessTokenJson(access_token)

users = {}
factsheets = []
for node in getGraphQl(getAllFactsheetsQuery(),access_token)['data']['allFactSheets']['edges']:
  factsheets.append({"id":node['node']['id'],"name":node['node']['name'],"type":node['node']['type']})

for fs in factsheets:
  response = getGraphQl(getUserCreate(fs['id']),access_token)['data']['allLogEvents']['edges'][0]
  
  userId = response['node']['user']['id']
  if (userId not in users):
    users[userId] = {"userName":response['node']['user']['userName'],"email":response['node']['user']['email'],"fs":[]}
  users[userId]['fs'].append(fs)

with open('usersToFactSheets.json', 'w') as outfile:  
  json.dump(users, outfile, indent=2, sort_keys=True)
