import json 
import requests 
import pandas as pd

api_token = '<TOKEN>'
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

# Delete the document
def createDocument(id, name, url):
  query = """
    mutation {
      createDocument(factSheetId: "%s", name: "%s", url: "%s", description: "", validateOnly: false) {
        id
      }
    } 
  """ % (id, name, url)
  print "create document " + id
  response = call(query)
  print response

# Start of the main program

df = pd.read_csv('Book1.csv',sep=';')
  
for index, row in df.iterrows():
  createDocument(row['id'], row['name'], row['url'])
