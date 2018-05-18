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
  print json_data
  response = requests.post(url=request_url, headers=header, data=json_data)
  response.raise_for_status()
  return response.json()

def createBCRelation(app, bc) :
  query = """
    mutation {
      updateFactSheet(id: "%s", 
                      patches: [{op: add, path: "/relApplicationToBusinessCapability/new_1", value: "{\\\"factSheetId\\\": \\\"%s\\\"}"}]) {
        factSheet {
          id
        } 
      }
    }
  """ % (app, bc)
  print "Create app - bc relation: " + app + "->" + bc
  call(query)

def createUGRelation(app, bc) :
  query = """
    mutation {
      updateFactSheet(id: "%s", 
                      patches: [{op: add, path: "/relApplicationToUserGroup/new_1", value: "{\\\"factSheetId\\\": \\\"%s\\\"}"}]) {
        factSheet {
          id
        } 
      }
    }
  """ % (app, bc)
  print "Create app - ug relation: " + app + "->" + bc
  call(query)

def createProcRelation(app, bc) :
  query = """
    mutation {
      updateFactSheet(id: "%s", 
                      patches: [{op: add, path: "/relApplicationToProcess/new_1", value: "{\\\"factSheetId\\\": \\\"%s\\\"}"}]) {
        factSheet {
          id
        } 
      }
    }
  """ % (app, bc)
  print "Create app - bc relation: " + app + "->" + bc
  call(query)

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

def deleteConstraint(fs, constrainedType, constrainedId, constrainingType, constrainingId) :
  query = """
    mutation {
      deleteRelationConstraint(factSheetId: "%s", constrainedRelationType: "%s", constrainedRelationTargetFactSheetId: "%s", constrainingRelationType: "%s", constrainingRelationTargetFactSheetId: "%s")
      {  
       id
      }
    }
  """ % (fs, constrainedType, constrainedId, constrainingType, constrainingId)
  print call(query)

def deleteConstraints(rel) :
  query = """
{
  allFactSheets(factSheetType: Application) {
  edges { node { id 
    ... on Application {
      relApplicationToProcess {
        edges {
          node {
            factSheet {id}
            constrainingRelations {
              relations {
                factSheet {
                  id
                }
              }
            }
          }
        }
      }
    }
  }}}
}
  """
  response = call(query)
  print response
  for appNode in response['data']['allFactSheets']['edges']:
    appId = appNode['node']['id']
    print appId
    for relationNode in appNode['node'][rel]['edges']:
      bcId = relationNode['node']['factSheet']['id']
      for constraint in relationNode['node']['constrainingRelations']['relations']:
        print deleteConstraint(appId, rel, bcId, 'relApplicationToUserGroup', constraint['factSheet']['id'])

# Start of the main logic

# 1. Read the input as a CSV
df = pd.read_csv('Book2.csv',sep=';')

#getConstraints()

# 4. Create the relations based on the saved ids
for index, row in df.iterrows():
 # if row['bc'] == row['bc']:
 #   createBCRelation(row['app'], row['bc'])
 # if row['ug'] == row['ug']:
 #   createUGRelation(row['app'], row['ug'])
 if row['bc'] == row['bc'] and row ['ug'] == row['ug']:
   createConstraint(row['app'], 'relApplicationToBusinessCapability', row['bc'], 'relApplicationToUserGroup', row['ug'])
 if row['process'] == row['process'] and row ['ug'] == row['ug']:
   createConstraint(row['app'], 'relApplicationToProcess', row['process'], 'relApplicationToUserGroup', row['ug'])
 if row['process'] == row['process'] and row ['bc'] == row['bc']:
   createConstraint(row['app'], 'relApplicationToProcess', row['process'], 'relApplicationToBusinessCapability', row['bc'])
 if row['process'] != row['process'] and row ['bc'] != row['bc'] and row['ug'] == row['ug']:
    createUGRelation(row['app'], row['ug'])
 if row['process'] != row['process'] and row ['bc'] == row['bc'] and row['ug'] != row['ug']:
    createBCRelation(row['app'], row['bc'])
 if row['process'] == row['process'] and row ['bc'] != row['bc'] and row['ug'] != row['ug']:
    createProcRelation(row['app'], row['process'])
