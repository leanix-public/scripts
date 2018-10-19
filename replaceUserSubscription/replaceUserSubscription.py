import json 
import requests 

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


def getAllSubscriptions(user):
  query = """
  {
    allFactSheets {
      edges {
        node {
          id
          subscriptions {
            edges {
              node {
                id
                user {
                  email
                }
                type
                roles {
                  id
                  comment
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
  subscriptions = []
  for fs in response['data']['allFactSheets']['edges']:
    for subscription in fs['node']['subscriptions']['edges']:
      if subscription['node']['user']['email'] == user:
        subscriptions.append({'id': subscription['node']['id'], 'fsId': fs['node']['id'], 'type': subscription['node']['type']})
  return subscriptions

def getRoles(fsId, user):
  query = """
  {
    factSheet(id: "%s") {
      id
      subscriptions {
        edges {
          node {
            user {
              email
            }
            roles {
              id
              comment
            }
          }
        }
      }
    }
  }
  """ % (fsId)
  response = call(query)
  for subscription in response['data']['factSheet']['subscriptions']['edges']:
    if subscription['node']['user']['email'] == user:
      return subscription['node']['roles']
  return []

def createSubscription(fsId, user, type, roles) :
  query = """
    mutation {
      createSubscription(factSheetId: "%s", user: {email: "%s"}, type: %s, roles: [%s]) {
        id
    }
  }
  """ % (fsId, user, type, roles)
  print("Create new subscription for: " + fsId)
  response = call(query)
  print(response)

def deleteSubscription(id, fsId) :
  query = """
    mutation {
      deleteSubscription(id: "%s") {
        id
    }
  }
  """ % (id)
  print("Delete old subscription for: " + fsId)
  response = call(query)
  print(response)

# Start of the main program
oldUser = 'srv.dordemo@meshlab.de'
newUser = 'cio.dordemo@meshlab.de'
for subscription in getAllSubscriptions(oldUser):

  roles = []
  for role in getRoles(subscription['fsId'], oldUser):
    roles.append("{id: \"" + role['id'] + "\", comment: \"" + (role['comment'] if role['comment'] != None else "") + "\"}")
  createSubscription(subscription['fsId'], newUser, subscription['type'],  ",".join(roles))

  deleteSubscription(subscription['id'], subscription['fsId'])

