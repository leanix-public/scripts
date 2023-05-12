import json 
import requests

api_token = ''
auth_url = 'https://<mtm_region>.leanix.net/services/mtm/v1/oauth2/token' 
request_url = 'https://<customer_domain>.leanix.net/services/pathfinder/v1/graphql'

# Define fact sheet type, relationship name and constraining relationship name
factsheetType = 'Project'
relationship = 'relProjectToBusinessCapability'
constrainingRelationship = 'relProjectToUserGroup'
        
response = requests.post(auth_url, auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'})
response.raise_for_status() 
access_token = response.json()['access_token']
auth_header = 'Bearer ' + access_token
header = {'Authorization': auth_header, 'Content-Type': 'application/json'}


# General function to call GraphQL given a query
def call(query):
  data = {"query" : query}
  json_data = json.dumps(data)
  response = requests.post(url=request_url, headers=header, data=json_data)
  return response.json()

def createConstraint(fs, constrainedType, constrainedId, constrainingType, constrainingId) :
  query = """
    mutation {
      createRelationConstraint(factSheetId: "%s", constrainedRelationType: "%s", constrainedRelationTargetFactSheetId: "%s", constrainingRelationType: "%s", constrainingRelationTargetFactSheetId: "%s")
      {  
       id
       name
      }
    }
  """ % (fs, constrainedType, constrainedId, constrainingType, constrainingId)
  print(call(query))

def fixConstraints(fsType='Project', rel='relProjectToBusinessCapability', constrainingRel='relProjectToUserGroup') :
  query = """
  { allFactSheets(factSheetType: %s) {
      edges { node { 
        id 
        name 
        ... on %s {
          %s {edges { node { factSheet { id name}}}}
          %s {edges { node { factSheet { id name}}}}
        }
      }}
  }}""" % (fsType, fsType, rel, constrainingRel)
  
  response = call(query)
  for fsNode in response['data']['allFactSheets']['edges']: # eg: Project
    fsId = fsNode['node']['id']
    fsName = fsNode['node']['name']
    for relFs in fsNode['node'][rel]['edges']: # eg: Business Capability
      relFsId = relFs['node']['factSheet']['id']
      relFsName = relFs['node']['factSheet']['name']
      for constrainRelFs in fsNode['node'][constrainingRel]['edges']: # eg: User Group
        constrainRelFsId = constrainRelFs['node']['factSheet']['id']
        constrainRelFsName = constrainRelFs['node']['factSheet']['name']
        print("""Creating constrinaning relation for '%s' between '%s' and '%s'""" %(fsName, relFsName, constrainRelFsName))
        createConstraint(fsId, rel, relFsId, constrainingRel, constrainRelFsId)
        
   
# Start of the main logic

fixConstraints(fsType=factsheetType, rel=relationship, constrainingRel=constrainingRelationship)
