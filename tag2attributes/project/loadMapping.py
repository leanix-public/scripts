import json 
import requests 
import pandas as pd

import itertools
import csv


"""
mtm_base_url = 'https://svc.leanix.net/services/mtm/v1' 
pathfinder_base_url = 'https://adidas.leanix.net/services/pathfinder/v1'
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


def getTags(access_token):
  #print("getTags Start")
  query = """
  {
    allTags {
      edges {
        node {
          name
          id
          tagGroup {
            name
            restrictToFactSheetTypes
            mode
          }
        }
      }
    }
  }
  """
  response = callGraphQL(query, access_token)
  #print(response)
  tags = []
  for tag in response['data']['allTags']['edges']:
    node = tag['node']
    if node['tagGroup'] and 'BusinessCapability' in node['tagGroup']['restrictToFactSheetTypes']:
      tags.append({'name':node['name'], 'id':node['id'], 'tagGroup': node['tagGroup']['name'], 'mode': node['tagGroup']['mode']})
  return sorted(tags, key=lambda k: "%s %s" % (k['tagGroup'].lower(), k['name'].lower()))

def getAttributes(access_token):
  fields = call('models/dataModel', access_token)['data']['factSheets']['BusinessCapability']['fields']

  attributes = []
  for k, values in {key:val for key, val in fields.items() if val['type'] == 'MULTIPLE_SELECT' or val['type'] == 'SINGLE_SELECT'}.items():
    for v in values['values']:
      attributes.append({'name': k, 'value': v, 'type': values['type']} )
  return sorted(attributes, key=lambda k: "%s %s" % (k['name'], k['value']))



# Start of the main program

access_token = getAccessToken(api_token)

with open('mapping.csv', 'w') as csvfile:
  writer = csv.writer(csvfile, delimiter=';')
  writer.writerow(['Tag Group', 'Tag', 'Mode', 'Tag ID', 'Attribute', 'Value', 'Type'])

  for t, a in itertools.zip_longest(getTags(access_token),getAttributes(access_token)):
    # print("enter loop")
    if (t and a):
      # print ("if")
      writer.writerow([t['tagGroup'], t['name'], t['mode'], t['id'], a['name'], a['value'], a['type']])
    elif (t):
      # print("elif1")
      writer.writerow([t['tagGroup'], t['name'], t['mode'], t['id'], '', '', ''])
    elif a:
      # print("elif2")
      writer.writerow(['', '', '', '', a['name'], a['value'], a['type']])
