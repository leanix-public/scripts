import json 
import pandas as pd
import lxpy
import requests
from os import environ

## Search User Base for a certain subscription role and adjust their Authorization level accordingly

config = lxpy.ClientConfiguration(
    base_url=environ.get('BASE_URL', 'customer.leanix.net'),
    api_token=environ.get('API_TOKEN', 'my-api-token')
)


# Creates the Json post that you send to the /idm/invite endpoint
def getInviteUserData(hostId, user, ws, authRole, updateMessage):
  data = {
   "host": {
       "id": hostId
   },
   "user": {
       "email": user
   },
   "workspace": {
       "id": ws
   },
   "permission": {
       "role": authRole
   },
   "message": updateMessage
  }
  return data


def getPermissionsPage(page, size):
  permissionlist = mtm.workspaces().get_permissions(id=mtm.get_workspace_from_access_token().id, sort='id', page=page, size=size)
  pages = (permissionlist.total // size) + 1
  return pages, permissionlist.data

def getPermissions():
  permissions=[]
  counter = 0
  pages = 1
  #Fetch all permissions
  while counter < pages:
    pages, permissionsList = getPermissionsPage(counter,100)
    permissions.extend(permissionsList)
    counter+=1
  return permissions

def inviteUser(updateUserInfo, silent):
  status, response = mtm.post('/idm/invite?silent='+silent,updateUserInfo)
  if status != 200: print("Error "+str(status) + " on "+updateUserInfo['user']['email'] + " - "+json.dumps((eval(response))))
  else: print("Invited "+updateUserInfo['user']['email'])
  return status, response

def setCollaborationNotifications(status):
  data = {
      "workspace": {
        "id": mtm.get_workspace_from_access_token().id
      },
      "featureId": "collaboration.notifications",
      "status": status,
      "quota": None,
      "scope": "workspace"
    }
  return mtm.post("/customFeatures",data)

def reducePermissionsToEmailAndStatus(permissions):
  reducedPermissions = {}
  for permission in permissions:
    reducedPermissions[permission.user.email] = permission.status
  return reducedPermissions

# START OF MAIN FUNCTION
# Authenticate with the give config Parameters
mtm = None
try:
  mtm = lxpy.Mtm(config)
except requests.exceptions.HTTPError as err:
  print(err)

# STEP 2: Declare the target authorization role that should be given (all caps)
authRole = 'VIEWER'

# Read in the CSV file in format: only one column with name 'email'
# STEP : Add the right path to the CSV file and make sure the right seperator is used
df = pd.read_csv('yazaki.csv', sep=';')
userList = {}

for index, row in df.iterrows():
  userList[row['email'].strip()] = authRole

#print(json.dumps(userList,indent=2))

# Fetch the userID and workspaceID associated with the API_TOKEN
uuid_host = mtm.get_user_from_access_token().id
wsId = mtm.get_workspace_from_access_token().id

# Allow invites for users not currently associated with the Workspace
allowNewInvites = False
inviteSilently = 'true'

# Fetch all the Permissions in the Workspace, to avoid unneccesary invites on large data lists

for user in userList:
     #checks whether new users are allowed to be invited  || whether the user already has a permission and can be invited
  #if (user not in reducedPermissions and allowNewInvites) or (user in reducedPermissions and reducedPermissions[user] not in ['INVITED','ACTIVE']):
    dataObject = getInviteUserData(uuid_host, user, wsId, userList[user], 'silent-invite' )
    inviteUser(dataObject, inviteSilently)

#setCollaborationNotifications("ENABLED")