import json 
import requests 
import pandas as pd

api_token = '<API Token>'
auth_url = 'https://app.leanix.net/services/mtm/v1/oauth2/token' 
url = 'https://svc.leanix.net/services/mtm/v1'
ws = '3eb07b2e-7ae1-4388-8a17-618ef89388a8'
account = '5b055c1b-2ea2-45bb-9305-486d831de4b5'
request_url = url + '/workspaces/' + ws +'/users?page=0' 

# Get the bearer token - see https://dev.leanix.net/v4.0/docs/authentication
response = requests.post(auth_url, auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'})
response.raise_for_status() 
access_token = response.json()['access_token']
auth_header = 'Bearer ' + access_token
header = {'Authorization': auth_header, 'Content-Type': 'application/json'}

# General function to call GraphQL given a query
def call(email):
  request_url = url + '/workspaces/' + ws +'/users?email=office.chwdemo@meshlab.de'
  response = requests.get(url=request_url, headers=header)
  response.raise_for_status()
  return response.json()

def getPermission(href):
  response = requests.get(url=url + href, headers=header)
  response.raise_for_status()
  return response.json()

def updateUser(id, user):
  response = requests.put(url=url + '/users/' + id, headers=header, data=json.dumps(user))
  response.raise_for_status()
  return response.json()

df = pd.read_csv('LeanIXUserUpdate.csv', sep=';')
print(df)

# for user in df.loc[:,'oldEmail']:
#   call(user)['data']
#     print(user['email'])


# for user in call()['data']:
#   if (df.)


# https://app.leanix.net/services/mtm/v1/users?email=office.chwdemo%40meshlab.de&page=1&size=30

#   workspaces = []
#   for link in user['links']:
#     if link['rel'] == 'permissions':
#       permissions = getPermission(link['href'])
#       for permission in permissions['data']:
#         if (permission['workspaceId'] != ws and permission['active']):
#           workspaces.append(permission['workspaceId'])
#   if (len(workspaces) > 0):
#     print ("ignored " + user['email'])
#     continue
  
#   if user['account']['id'] != account:
#     print (user['id'])
#     user['account']['id'] = account  
#     #updateUser(user['id'], user) 
#     print (user) 

