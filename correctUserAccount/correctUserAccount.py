import json 
import requests 
import pandas as pd
import os


"""
api_token = '<API Token>'
auth_url = 'https://app.leanix.net/services/mtm/v1/oauth2/token' 
url = 'https://svc.leanix.net/services/mtm/v1'
ws = '3eb07b2e-7ae1-4388-8a17-618ef89388a8'
account = '5b055c1b-2ea2-45bb-9305-486d831de4b5'
request_url = url + '/workspaces/' + ws +'/users?page=0' 
"""

#INPUT
auth_url = "Placeholder"
request_url = "Placeholder"

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

    if choice == "10":
        url = 'https://demo-' + instance + '-svc.leanix.net/services/mtm/v1'
    else:
        url = 'https://' + instance + '-svc.leanix.net/services/mtm/v1'

except NameError:
    print("")
    print("Invalid input. Please enter a number.")
    print("")
    exit()

try:
    ws = input("Please enter the workspace-id: ")
except ValueError:
    print("")
    print("Invalid input.")
    print("")

try:
    account = input("Please enter the account-id: ")
except ValueError:
    print("")
    print("Invalid input.")
    print("")

request_url = url + '/workspaces/' + ws +'/users?page=0' 


#LOGIC
# Get the bearer token - see https://dev.leanix.net/v4.0/docs/authentication
response = requests.post(auth_url, auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'})
response.raise_for_status() 
access_token = response.json()['access_token']
auth_header = 'Bearer ' + access_token
header = {'Authorization': auth_header, 'Content-Type': 'application/json'}

# General function to call GraphQL given a query
def call():
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


for user in call()['data']:
  workspaces = []
  for link in user['links']:
    if link['rel'] == 'permissions':
      permissions = getPermission(link['href'])
      for permission in permissions['data']:
        if (permission['workspaceId'] != ws and permission['active']):
          workspaces.append(permission['workspaceId'])
  if (len(workspaces) > 0):
    print ("ignored " + user['email'])
    continue
  
  if user['account']['id'] != account:
    print (user['id'])
    user['account']['id'] = account  
    #updateUser(user['id'], user) 
    print (user) 

