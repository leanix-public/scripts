import json 
import requests 
import pandas as pd

api_token = '<API Token>'
auth_url = 'https://app.leanix.net/services/mtm/v1/oauth2/token' 
request_url = 'https://svc.leanix.net/services/mtm/v1/workspaces/3eb07b2e-7ae1-4388-8a17-618ef89388a8/users?page=0' 
putrequest = 'https://svc.leanix.net/services/mtm/v1/users/'

# Get the bearer token - see https://dev.leanix.net/v4.0/docs/authentication
response = requests.post(auth_url, auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'})
response.raise_for_status() 
access_token = response.json()['access_token']
auth_header = 'Bearer ' + access_token
header = {'Authorization': auth_header}

# General function to call GraphQL given a query
def call():
  response = requests.get(url=request_url, headers=header)
  response.raise_for_status()
  return response.json()

def put(query, userid):
  response = requests.put(url=putrequest+userid, headers=header, data=query)
  response.raise_for_status()
  return response.json()


def getQueryString(username, email, role):
  query = """ 
    {
      'account': {
          'id': '5b055c1b-2ea2-45bb-9305-486d831de4b5'
      },
      'userName': '%s',
      'email': '%s',
      'role': '%s',
      'status': 'ACTIVE'
    }"""%(username, email, role)
  return query


# for user in call()['data']:
#   print (user['id'] + " " + user['userName'])

print(put(getQueryString('cio.chwdemo@meshlab.de', 'cio.chwdemo@meshlab.de', 'ACCOUNTUSER'),'1575d016-48f2-4043-a3dd-bb16b1d3cffd'))
#print( getQueryString('cio.chwdemo@meshlab.de', 'cio.chwdemo@meshlab.de', 'ACCOUNTUSER'))   

# {
#     "account": {
#  "id": "5b055c1b-2ea2-45bb-9305-486d831de4b5"
# },
# "userName": "cio.chwdemo@meshlab.de",
#     "email": "testcio.chwdemo@meshlab.de",
#     "role": "ACCOUNTUSER",
#     "status": "ACTIVE"

#   }