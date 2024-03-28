import json 
import requests 
import pandas as pd


"""
api_token = '<API Token>'
workspace_id = '<Your Workspace ID>'

auth_url = 'https://eu-svc.leanix.net/services/mtm/v1/oauth2/token' 
request_url = 'https://eu-svc.leanix.net/services/mtm/v1/workspaces/%s/users?page=0'%(workspace_id) 
"""


#INPUT
auth_url = "Placeholder"
request_url = "Placeholder"

api_token = input("Enter your API-Token: ")

try:
    workspace_id = input("Please enter your workspace id: ")
except ValueError:
    print("")
    print("Invalid input.")
    print("")

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

    request_url = 'https://' + instance + '-svc.leanix.net/services/mtm/v1/workspaces/%s/users?page=0'%(workspace_id) 

except NameError:
    print("")
    print("Invalid input. Please enter a number.")
    print("")
    exit()


# Get the bearer token - see https://dev.leanix.net/v4.0/docs/authentication
response = requests.post(auth_url, auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'})
response.raise_for_status() 
access_token = response.json()['access_token']
auth_header = 'Bearer ' + access_token
header = {'Authorization': auth_header}

# General function to call GraphQL given a query
def call():
  response = requests.get(url=request_url, headers=header)
  response.raise_for_status()
  return response.json()

for user in call()['data']:

  print (user['id'] + " " + user['userName'])
