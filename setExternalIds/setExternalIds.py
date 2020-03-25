import json
import requests
import pandas as pd

api_token = '<API-TOKEN>'
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
    data = {"query": query}
    json_data = json.dumps(data)
    response = requests.post(url=request_url, headers=header, data=json_data)
    return response.json()


# Update the costs attribute on the existing relation
def setQuery():
    query = """
          mutation {
        updateFactSheet(id: "28fe4aa2-6e46-41a1-a131-72afb3acf256"
          patches: [{op: add, path: "/myJensExternalId",
            value: "{\"externalId\": \"10000\", \"forceWrite\": true}"}]
         
        ) {
          factSheet {
            ... on Application {
              myJensExternalId {
                externalId
              }
            }
          }
        }
      }
        """
    return query


# Start of the main program

# 1. Read the input
query = setQuery()
response = call(query)
print(response)
