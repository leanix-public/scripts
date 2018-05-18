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

def createConstraint(fs, constrainedType, constrainedId, constrainingType, constrainingId) :
  query = """
    mutation {
      createRelationConstraint(factSheetId: "%s", constrainedRelationType: "%s", constrainedRelationTargetFactSheetId: "%s", constrainingRelationType: "%s", constrainingRelationTargetFactSheetId: "%s")
      {  
       id
      }
    }
  """ % (fs, constrainedType, constrainedId, constrainingType, constrainingId)
  print call(query)

def fixConstraints() :
  query = """
{
  allFactSheets(factSheetType: Project) {
  edges { node { id 
    ... on Project {
      relProjectToBusinessCapability {
        edges {
          node {
            factSheet {id}
          }
        }
      }
      relProjectToUserGroup {
        edges {
          node {
            factSheet {id}
          }
        }
      }
    }
  }}}
}
  """
  response = call(query)
  for projectNode in response['data']['allFactSheets']['edges']:
    projectId = projectNode['node']['id']
    for bcNode in projectNode['node']['relProjectToBusinessCapability']['edges']:
      bcId = bcNode['node']['factSheet']['id']
      for ugNode in projectNode['node']['relProjectToUserGroup']['edges']:
        ugId = ugNode['node']['factSheet']['id']
        createConstraint(projectId, "relProjectToBusinessCapability", bcId, "relProjectToUserGroup", ugId)
        
   
# Start of the main logic

fixConstraints()
