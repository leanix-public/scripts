import json 
import requests 
import pandas as pd
import lxpy

        
config = lxpy.ClientConfiguration(
            base_url=os.environ.get('BASE_URL', ''),
            api_token=os.environ.get('API_TOKEN', '')
        )
pathfinder = lxpy.Pathfinder(config)


# General function to call GraphQL given a query
def call(query):
  data = {"query" : query}
  response = pathfinder.graphql().process_graph_ql(data)
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
