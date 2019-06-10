import json 
import requests 
import pandas as pd

api_token = '<API-Token>'
auth_url = 'https://app.leanix.net/services/mtm/v1/oauth2/token' 
request_url = 'https://svc.leanix.net/services/mtm/v1/workspaces/' 
request_event_url = "https://svc.leanix.net/services/mtm/v1/users/"


workspace_id = "<WS-ID>"

# Get the bearer token - see https://dev.leanix.net/v4.0/docs/authentication
response = requests.post(auth_url, auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'})
response.raise_for_status() 
access_token = response.json()['access_token']
auth_header = 'Bearer ' + access_token
header = {'Authorization': auth_header}

# General function to call GraphQL given a query
def callEvent(workspaceId):
  response = requests.get(url=request_url + workspaceId + '/events?since=2018-01-01T00%3A00%3A00.000Z&page=0', headers=header)
  response.raise_for_status()
  return response.json()

events = callEvent(workspace_id)['data']
for event in events:
  if event['type'] == 'USER_PERMISSION_UPDATE' and event['workspace']['id'] == workspace_id and event['user']['email']:
    print ('On ' + event['createdAt'] + ' '  + event['actor']['userName'] + ' changed the permission of the following user: ' + event['payload']['user']['userName'] + ' to ' + event['payload']['role'])
  