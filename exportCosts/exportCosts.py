import json 
import requests 
import csv

api_token = ''
auth_url = 'https://app.leanix.net/services/mtm/v1/oauth2/token' 
request_url = 'https://app.leanix.net/services/pathfinder/v1/graphql' 

# Get the bearer token - see https://dev.leanix.net/v4.0/docs/authentication
response = requests.post(auth_url, auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'})
response.raise_for_status() 
access_token = response.json()['access_token']
auth_header = 'Bearer ' + access_token
header = {'Authorization': auth_header}

# General function to call GraphQL given a query
def call(query):
  data = {"query" : query}
  json_data = json.dumps(data)
  response = requests.post(url=request_url, headers=header, data=json_data)
  response.raise_for_status()
  return response.json()

# Read all existing Application - IT Component relations
def exportCosts():
  query = """
  {
    allFactSheets(factSheetType: Application) {
      edges {
        node {
          id
          displayName
          ... on Application {
            relApplicationToITComponent {
              edges {
                node {
                  id
                  costTotalAnnual
                  factSheet {
                    id
                    displayName
                  }
                }
              }
            }
          }
        }
      }
    }
  }
  """
  response = call(query)

  with open('result.csv', 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=';')
    writer.writerow(['App ID', 'App Display Name', 'ITC ID', 'ITC Display Name', 'Total Annual Costs'])
  
    for appNode in response['data']['allFactSheets']['edges']:
      appId = appNode['node']['id']
      appName = appNode['node']['displayName']
      for relationNode in appNode['node']['relApplicationToITComponent']['edges']:
        costs = relationNode['node']['costTotalAnnual']
        itcId = relationNode['node']['factSheet']['id']
        itcName = relationNode['node']['factSheet']['displayName']     
        writer.writerow([appId, appName, itcId, itcName, costs])

exportCosts()