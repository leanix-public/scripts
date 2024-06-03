import json 
import requests 
import os
import logging

import itertools
import csv


logging.basicConfig(level=logging.INFO)

#Request timeout
TIMEOUT = 20

#API token and subdomain set as env variables
LEANIX_API_TOKEN = os.getenv('LEANIX_API_TOKEN')
LEANIX_SUBDOMAIN = os.getenv('LEANIX_SUBDOMAIN')

LEANIX_AUTH_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net/services/mtm/v1' 
LEANIX_REQUEST_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net/services/pathfinder/v1'

"""
mtm_base_url = 'https://svc.leanix.net/services/mtm/v1' 
pathfinder_base_url = 'https://adidas.leanix.net/services/pathfinder/v1'
"""

mtm_base_url = LEANIX_AUTH_URL
pathfinder_base_url = LEANIX_REQUEST_URL
api_token = LEANIX_API_TOKEN


#Authorization
def getAccessToken(api_token):
  #different than callPost since it needs to send the auth_header
  response = requests.post(mtm_base_url+"/oauth2/token", auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'}, timeout=TIMEOUT)
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
  response = requests.post(url=pathfinder_base_url + '/graphql', headers=getHeader(access_token), data=json_data, timeout=TIMEOUT)
  response.raise_for_status()
  #print("requested")
  return response.json()

def call(url, access_token):
  response = requests.get(url=pathfinder_base_url + '/' + url, headers=getHeader(access_token), timeout=TIMEOUT)
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
