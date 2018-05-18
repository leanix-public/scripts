import json 
import requests 
import pandas as pd

api_token = '<api token>'
auth_url = 'https://app.leanix.net/services/mtm/v1/oauth2/token' 
request_url = 'https://app.leanix.net/services/pathfinder/v1/bookmarks/<bookmark id>' 

# Get the bearer token - see https://dev.leanix.net/v4.0/docs/authentication
response = requests.post(auth_url, auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'})
response.raise_for_status() 
access_token = response.json()['access_token']
auth_header = 'Bearer ' + access_token
header = {'Authorization': auth_header, 'Content-Type': 'application/json'}

# General function to call GraphQL given a query
def call():

  data = {}
  data['name'] = "Test Dashboard"
  data['type'] = "DASHBOARD"
  data['sharing'] = "SYSTEM"

  panel1 = {}
  panel1["titleKey"] = "chart"
  panel1["type"] = "CHART"
  panel1["titleKey"] = "chart"
  panel1["options"] = {"chartType": "column", "tagGroupId": "1b5cbcee-3251-4be1-8a46-13a5c82a03fc", 
    "filter": { "facetFilter": []}}
  
  data["state"] = {
    "config": 
      {"rows": 
        [{"columns": 
          [{ "width": "6", 
            "rows": [{"panels": [panel1, panel1]}]
           },
           { "width": "6", 
            "rows": [{"panels": [panel1, panel1]}]
           }
          ]
        }]
      }
    }
  
  json_data = json.dumps({"data": data})
 
  response = requests.put(url=request_url, headers=header, data=json_data)

  response.raise_for_status()
  return response.json()


print call()
