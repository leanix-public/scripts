import json 
import requests 
import pandas as pd
import math
import json
from os import environ


"""
mtm_base_url = 'https://svc.leanix.net/services/mtm/v1' 
pathfinder_base_url = 'https://abc.leanix.net/services/pathfinder/v1'
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


#Authorization
def getAccessToken(api_token):
  #different than callPost since it needs to send the auth_header
  response = requests.post(mtm_base_url+"/oauth2/token", auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'})
  response.raise_for_status() 
  access_token = response.json()['access_token']
  return access_token

def getHeader(access_token):
  return {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}

# General function to call GraphQL given a query
def callGraphQL(query, access_token):
  #print("callGraphQl")
  data = {"query" : query}
  json_data = json.dumps(data)
  #print("request")
  response = requests.post(url=pathfinder_base_url + '/graphql', headers=getHeader(access_token), data=json_data)
  response.raise_for_status()
  #print("requested")
  return response.json()

def call(url, access_token):
  response = requests.get(url=pathfinder_base_url + '/' + url, headers=getHeader(access_token))
  response.raise_for_status()
  return response.json()


# Read all existing Application - IT Component relations
# Comment from CHZ: while variables isn't needed in the query here,
# leaving it in the query so others know it's an option
def getAllApps(access_token):
  query = """
  {
    allFactSheets(factSheetType: BusinessCapability) {
      edges {
        node {
          id
          tags { id name tagGroup {name} }
        }
      }
    }
  }
  """
  response = callGraphQL(query, access_token)
  return(response)
 

# Start of the main program
access_token = getAccessToken(api_token)
df = pd.read_csv('mapping.csv', sep=';')

apps = getAllApps(access_token)
for appNode in apps['data']['allFactSheets']['edges']:
  tags = list(map(lambda x: x['id'], appNode['node']['tags']))
  
  patches = []
  multiSelects = {}

  for index, row in df.iterrows():
    if (row['Tag ID'] in tags):
      tags.remove(row['Tag ID'])

      if (row['Type'] == 'SINGLE_SELECT'):
        patches.append("{op: add, path: \"/" + row['Attribute'] + "\", value: \""+ row['Value'] + "\"}")
      elif (row['Type'] == 'MULTIPLE_SELECT'):
        if (row['Attribute'] not in multiSelects):
          multiSelects[row['Attribute']] = []
        multiSelects[row['Attribute']].append(row['Value'])

  for k, v in multiSelects.items():
    multiSelectString = ",".join(map( lambda x: '\\\"' + x + '\\\"', v))
    patches.append("{op: replace, path: \"/"+ k +"\", value: \"["+ multiSelectString +"]\"}")

  tagString = ",".join(map(lambda x: '{\\\"tagId\\\": \\\"' + x + '\\\"}', tags))
  patches.append("{op: replace, path: \"/tags\", value: \"["+ tagString + "]\"}")

  query = """
      mutation {
        updateFactSheet(id: "%s", patches: [%s]) {
          factSheet {
            id
          } 
        }
      }
    """ % (appNode['node']['id'], ",".join(patches))
  print (query)
  response = callGraphQL(query, access_token)
  print (response)

