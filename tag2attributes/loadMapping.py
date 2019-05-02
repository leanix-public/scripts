import json 
import requests 
import pandas as pd

import itertools
import csv

api_token = '<API-TOKEN>'
auth_url = 'https://app.leanix.net/services/mtm/v1/oauth2/token' 
request_url = 'https://app.leanix.net/services/pathfinder/v1' 

# Get the bearer token - see https://dev.leanix.net/v4.0/docs/authentication
response = requests.post(auth_url, auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'})
response.raise_for_status() 
access_token = response.json()['access_token']
auth_header = 'Bearer ' + access_token
header = {'Authorization': auth_header}

# General function to call GraphQL given a query
def callGraphQL(query):
  data = {"query" : query}
  json_data = json.dumps(data)
  response = requests.post(url=request_url + '/graphql', headers=header, data=json_data)
  response.raise_for_status()
  return response.json()

def call(url):
  response = requests.get(url=request_url + '/' + url, headers=header)
  response.raise_for_status()
  return response.json()


def getTags():
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
  response = callGraphQL(query)
  tags = []
  for tag in response['data']['allTags']['edges']:
    node = tag['node']
    if node['tagGroup'] and 'Application' in node['tagGroup']['restrictToFactSheetTypes']:
      tags.append({'name':node['name'], 'id':node['id'], 'tagGroup': node['tagGroup']['name'], 'mode': node['tagGroup']['mode']})
  return sorted(tags, key=lambda k: "%s %s" % (k['tagGroup'].lower(), k['name'].lower()))

def getAttributes():
  fields = call('models/dataModel')['data']['factSheets']['Application']['fields']

  attributes = []
  for k, values in {key:val for key, val in fields.items() if val['type'] == 'MULTIPLE_SELECT' or val['type'] == 'SINGLE_SELECT'}.items():
    for v in values['values']:
      attributes.append({'name': k, 'value': v, 'type': values['type']} )
  return sorted(attributes, key=lambda k: "%s %s" % (k['name'], k['value']))

# Start of the main program


with open('mapping.csv', 'w') as csvfile:
  writer = csv.writer(csvfile, delimiter=';')
  writer.writerow(['Tag Group', 'Tag', 'Mode', 'Tag ID', 'Attribute', 'Value', 'Type'])
   
  for t, a in itertools.zip_longest(getTags(),getAttributes()):
    if (t and a):
      writer.writerow([t['tagGroup'], t['name'], t['mode'], t['id'], a['name'], a['value'], a['type']])
    elif (t):
      writer.writerow([t['tagGroup'], t['name'], t['mode'], t['id'], '', '', ''])
    elif a:
      writer.writerow(['', '', '', '', a['name'], a['value'], a['type']])
