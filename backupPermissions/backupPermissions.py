import json 
import requests 
import pandas as pd
#import base64

import csv

## Search User Base for a certain subscription role and adjust their Authorization level accordingly
auth_url = 'https://app.leanix.net/services/mtm/v1/oauth2/token' 
url_base = 'https://svc.leanix.net/services/mtm/v1'

def getWorkspaceData(workspaceName):
  with open('access.json') as json_file:  
    data = json.load(json_file)
    return data[workspaceName]

def getPermissionUrl(workspaceId,page):
  return url_base + '/workspaces/' + workspaceId +'/permissions?page='+str(page)+'&size=100'

# Get the bearer token - see https://dev.leanix.net/v4.0/docs/authentication
header = ''
def authenticate(workspaceName):
  api_token= getWorkspaceData(workspaceName)['apitoken']
  response = requests.post(auth_url, auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'})
  response.raise_for_status() 
  access_token = response.json()['access_token']
#  print(access_token)
#  tokenjson = base64.b64decode(access_token)
#  print(str(tokenjson))
  auth_header = 'Bearer ' + access_token
  header = {'Authorization': auth_header, 'Content-Type': 'application/json'}
  return header

def savePermissions(workspace, permissions):
  with open(workspace+'.json', 'w') as outfile:  
    json.dump(permissions, outfile, indent=2, sort_keys=True)

def getPermissions(workspaceId,header):
  permissions = []
#  response = requests.get(url=getPermissionUrl(workspaceId), headers=header)
#  response.raise_for_status()
  for x in range(1,170):
    response = requests.get(url=getPermissionUrl(workspaceId,x), headers=header)
    response.raise_for_status()
    permissions.extend(response.json()['data'])

  return permissions

def saveUserInfo(workspaceName, permissions):
  with open(workspaceName+'Info.csv', 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=';')
    writer.writerow(['email', 'role', 'status'])
    for permission in permissions:
      writer.writerow([permission['email'],permission['role'],permission['status']])

def saveUserInfoJson(workspaceName, permissions):
  reducedPerm = {}
  for permission in permissions:
    reducedPerm[permission['email']] = {'email':permission['email'],'role':permission['role'],'status':permission['status']}
  with open(workspaceName+'Info.json', 'w') as outfile:
    json.dump(reducedPerm, outfile, indent=2, sort_keys=True)

def getUserInfo(workspaceName, permissions):
  data = []
  for permission in permissions:
    data.append({'email':permission['user']['email'], 'role':permission['role'],'status':permission['status']})
  return data

def updatePermissions(header,permission):
  try:
    response = requests.post(url=url_base+'/permissions', headers=header, data=json.dumps(permission))
    response.raise_for_status()
  except requests.exceptions.HTTPError as err:
    print(err)
    print(permission['user']['id'] + ";"+ permission['user']['email'])
    if err.response.status_code==401:
      header=authenticate(workspaceName)
      response = updatePermissions(header,permission)
      return response
  return response.json()

def loadAndUpdatePermissions():
  existing = {}
  counter = 0
  with open('BoschSandboxNewInfo.json') as json_file:
    existing = json.load(json_file)

  permission = {}
  with open('boschsand.json') as json_file:
    permissions = json.load(json_file)
  for permission in reversed(permissions):
#      permission = data[0]
    permission.pop('id')
    if permission['status'] == 'ACTIVE':
      permission['status'] = 'INVITED'
      if permission['user']['email'] not in existing:
        counter+=1
        updatePermissions(header,permission)
        print(counter)




workspaceName = 'boschpflive'
workspace = getWorkspaceData(workspaceName)
#print(workspace)
header = authenticate(workspaceName)

permissions = getPermissions(workspace['workspaceId'],header)
#userInfo = getUserInfo(workspaceName,permissions)
#saveUserInfoJson(workspaceName, userInfo)
savePermissions(workspaceName+"2",permissions)
#loadAndUpdatePermissions()



# STEP 1: Get Super API Token of the WS for which you are changing Users
#api_token = '9FFCW6xZwYffrxVZ7GjP2JneOkyRnS7ksRSvSNvp'
# STEP 2: Get the WS ID for which you are making the changes
#ws = '3eb07b2e-7ae1-4388-8a17-618ef89388a8'
# UUID of the Super User support@leanix.net
#uuid_host = '1e3f0aef-b870-4320-be28-c0412f8db088'

#getPermission_url = url + '/workspaces/' + ws +'/permissions?page=0' 
#postInvite_url = url + '/idm/invite?silent='  

# STEP 3: Declare the subscription role that is being filtered by

# STEP 4: Declare the target authorization role that should be given (all caps)
#authRole = 'MEMBER'

# Get the bearer token - see https://dev.leanix.net/v4.0/docs/authentication
# response = requests.post(auth_url, auth=('apitoken', api_token),
#                          data={'grant_type': 'client_credentials'})
# response.raise_for_status() 
# access_token = response.json()['access_token']
# auth_header = 'Bearer ' + access_token
# header = {'Authorization': auth_header, 'Content-Type': 'application/json'}


# #UpdateUserInfo = the data object sent for the invite request as created in getInviteUserData()
# #silent = are notifications sent (true/false) as string
# def inviteUser(updateUserInfo, silent):
#   response = requests.post(url=postInvite_url + silent, headers=header, data=updateUserInfo)
#   response.raise_for_status()
#   return response.json()



# START OF MAIN FUNCTION
# Read in the CSV file in format (oldMail;newMail)
# STEP 3: Add the right path to the CSV file and make sure the right seperator is used
#df = pd.read_csv('target.csv', sep=';')

# userList = []

# for index, row in df.iterrows():
#   userList.append(row['email'])

# # Iterate through the call response and change the Email-Adress
# for user in call()['data']:
#   if user['user']['email'] in userList:
#     dataObject = getInviteUserData(uuid_host, user['user']['email'], ws, authRole, 'silent-invite' )
#     print(dataObject)
#     print(inviteUser(dataObject))
