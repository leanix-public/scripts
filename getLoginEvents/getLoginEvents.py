import json 
import requests 
import pandas as pd

api_token = '<TOKEN>'
auth_url = 'https://app.leanix.net/services/mtm/v1/oauth2/token' 
request_url = 'https://svc.leanix.net/services/mtm/v1/workspaces/' 
request_event_url = "https://svc.leanix.net/services/mtm/v1/users/"


workspace_id = "<WS_ID>"

# Get the bearer token - see https://dev.leanix.net/v4.0/docs/authentication
response = requests.post(auth_url, auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'})
response.raise_for_status() 
access_token = response.json()['access_token']
auth_header = 'Bearer ' + access_token
header = {'Authorization': auth_header}

# General function to call GraphQL given a query
def callUser(workspaceId):
  response = requests.get(url=request_url + workspaceId + '/users?page=0', headers=header)
  response.raise_for_status()
  return response.json()

def callEvent(userId):
  response = requests.get(url=request_event_url + userId + '/events?since=2018-01-01T00%3A00%3A00.000Z&page=0', headers=header)
  response.raise_for_status()
  return response.json()

def callPermissions(link):
  response = requests.get(url="https://svc.leanix.net/services/mtm/v1" + link, headers=header)
  response.raise_for_status()
  return response.json()

users = callUser(workspace_id)['data']
print ("Processed " + str(len(users)) + " users")
for user in users:
    events = callEvent(user['id'])['data']
    
    permissionUpdated = False
    welcomeSSO = False
    for event in events:

        if event['type'] == 'USER_PERMISSION_UPDATE' and event['workspace']['id'] == workspace_id :
            permissionUpdated = True
            print ('USER_PERMISSION_UPDATE ' + user['id'] + ' ' + user['email'] + ' ' + event['payload']['role'] + ' ' + event['createdAt']) 
        if event['type'] == 'USER_WELCOME_SSO' and event['workspace']['id'] == workspace_id:
            welcomeSSO = True

    if (welcomeSSO and not permissionUpdated):
        for link in user['links']:
            if (link['rel'] == 'permissions'):
                for permission in callPermissions(link['href'])['data']:
                    if (permission['workspaceId'] == workspace_id):
                        print ('USER_WELCOME_SSO ' + user['id'] + ' ' + user['email'] + ' ' + permission['role'] + ' ' + permission['lastLogin']) 
     