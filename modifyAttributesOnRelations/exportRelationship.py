# This Script can be used to export the relationships between two FactSheets along with the attributes on the relation.
# In this example we are looking at Application to ITC Relationship and Attribute on Relationship : technicalSuitability or Technical Fit.
# This script will export the fields, Application,ITC, Application to ITC Relationship and also the attribute technicalSuitability
# Output of this script is a file : Info.csv can be used as an input in importRelationship.py after making the relvant changes.
# Changes required in the Script :-
# 1. Adapt mtm_base_url as per your instance. Eg. us-svc,eu-svc
# 2. Adapt pathfinder_base_url and apiToken
# 3. Modify the query in getRelationVariablesToExport and include the attributes as per requirement.
# 4. Also modify the CSV writer and newObject to include your attributes.

import json 
import requests 
import pandas as pd
import base64
import time
import csv
import datetime


"""
# 1. Adapt mtm_base_url as per your instance. Eg. us-svc,eu-svc
mtm_base_url = 'https://eu-svc.leanix.net/services/mtm/v1'
# 2. Adapt pathfinder_base_url
pathfinder_base_url = 'https://demo-eu.leanix.net/services/pathfinder/v1'
apiToken = ""
"""

#INPUT
mtm_base_url = "Placeholder"
pathfinder_base_url = "Placeholder"

apiToken = input("Enter your API-Token: ")

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

    if instance == 10:
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

def callPost(request_url, header, data):
  try:
    response = requests.post(url=request_url, headers=header,  data=json.dumps(data))
    response.raise_for_status()
  except requests.exceptions.HTTPError as err:
    print(request_url)
    print(json.dumps(data))
    print(err)
    exit
  return response.json()



def updateHost(host):
  global pathfinder_base_url
  pathfinder_base_url = 'https://%s/services/pathfinder/v1'%(host)

def getApiToken():
  with open('../access.json') as json_file:  
    data = json.load(json_file)
#    if (data["host"] is not None):
#      updateHost(data["host"])
    return data['apiTokenExportRelations']

def postGraphQl(query, access_token):
  response = callPost(pathfinder_base_url+'/graphql', getHeader(access_token), query)
  return response



def getRelationVariablesToExport():
  query = """
      {
      allFactSheets(factSheetType: Application){
        totalCount
        edges{
          node{
            id
            displayName
            tags{
              id
              name
            }
            ... on Application{
              relApplicationToITComponent{
                edges{
                  node{
                    id
                    factSheet{
                      displayName
                      id
                    }
                    technicalSuitability
                  }
                }
            }
          }
        }
      }

    }
    }

  """
  return {"query": query}

def getSingleFactsheet():
  query = """{    
  factSheet(id:"28fe4aa2-6e46-41a1-a131-72afb3acf256") {
            id
            displayName
            ... on Application{
              relApplicationToUserGroup{
                edges{
                  node{
                    id
                    activeFrom
                    activeUntil
                  }
                }
              }
            }
          }
}
"""
  return {"query": query}



def getGraphQl(query, access_token):
  response = callPost(pathfinder_base_url+'/graphql', getHeader(access_token), query)
  return response


access_token = getAccessToken(apiToken)
access_token_json = getAccessTokenJson(access_token)


## notice the Dictionary Call ['data'] at the end ofhe function call.
data = getGraphQl(getRelationVariablesToExport(), access_token)['data']

#print(json.dumps(data,indent=2))

with open('Info.csv', 'w') as csvfile:
  #writer = csv.writer(csvfile, delimiter=';') #For German Locale, we need another delimiter
  writer = csv.writer(csvfile, delimiter=';')
  writer.writerow(['Application','App ID', 'ITComponent', 'ITComponent ID','Relation ID', 'Tags','Attribute Value'])

  for fsnode in data['allFactSheets']['edges']:
    fs = fsnode['node']
    tags = fs['tags']
    tagCots = ''
    for tag in tags:
      if tag['name'] == 'COTS Package':
        tagCots = 'COTS Package'
      if tag['name'] == 'No COTS Package':
        tagCots = 'No COTS Package'
    for dateNode in fs['relApplicationToITComponent']['edges']:
      newObject = {
        "application":fs['displayName'],
        "appId":fs['id'],
        "relationId":dateNode['node']['id'],
        "itcName":dateNode['node']['factSheet']['displayName'],
        "itcId":dateNode['node']['factSheet']['id'],
        "attributeValue":dateNode['node']['technicalSuitability'],
        "tagCots":tagCots
      }
      writer.writerow([newObject['application'],newObject['appId'],newObject['itcName'],newObject['itcId'],newObject['relationId'],newObject['tagCots'],newObject['attributeValue']])