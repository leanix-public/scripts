import json 
import requests 
import pandas as pd

api_token = 'TOKEN'
auth_url = 'https://app.leanix.net/services/mtm/v1/oauth2/token' 
request_url = 'https://app.leanix.net/services/pathfinder/v1/bookmarks' 

# Get the bearer token - see https://dev.leanix.net/v4.0/docs/authentication
response = requests.post(auth_url, auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'})
response.raise_for_status() 
access_token = response.json()['access_token']
auth_header = 'Bearer ' + access_token
header = {'Authorization': auth_header, 'Content-Type': 'application/json'}
  
def getPanel(filters, title, chartType, tagGroupId, singleSelectField):
  panel1 = {}
  panel1["title"] = title
  panel1["type"] = "CHART"
  panel1["options"] = {"chartType": chartType, "tagGroupId": tagGroupId, "singleSelectField": singleSelectField, "filter":  getFilter(filters) }
  return panel1

def getFilter(filters):
  facetFilters = { "facetFilter": [{
                  "keys": [
                      "Application"
                  ],
                  "facetKey": "FactSheetTypes",
                  "operator": "OR"
              },
              {
                  "keys": [
                      "active",
                      "phaseOut"
                  ],
                  "facetKey": "lifecycle",
                  "operator": "OR",
                  "dateFilter": {
                      "to": "2018-01-29",
                      "from": "2018-05-24",
                      "type": "TODAY",
                      "maxDate": "2023-03-31",
                      "minDate": "2003-01-01"
                  }
              },
              {
                  "keys": [
                      "a819eb5e-7963-46b0-8329-b43ff93b603d"
                  ],
                  "facetKey": "Application Type",
                  "operator": "OR"
              },
              {
                  "keys": [
                      "333ca077-25e4-4aaf-a9f1-94e7d2650d97"
                  ],
                  "facetKey": "CostCentre",
                  "operator": "OR"
              }]
          }
  for k,v in filters.items():
    facetFilters['facetFilter'].append({"facetKey": k, "keys": [ v ], "operator": "OR"})
  return facetFilters

df = pd.read_excel('input.xlsx', sheetname='Worksheet', sep=';')
file_name = './dashboards.json'
with open(file_name, 'r') as f:
    dashboards = json.load(f)

for d in dashboards:
  d['singleSelectField'] = '' if not 'singleSelectField' in d else d['singleSelectField']
  d['singleSelectField2'] = '' if not 'singleSelectField2' in d else d['singleSelectField2']
 
  d['tagGroupId'] = '' if not 'tagGroupId' in d else d['tagGroupId']
  d['tagGroupId2'] = '' if not 'tagGroupId2' in d else d['tagGroupId2']
  d['title2'] = '' if not 'title2' in d else d['title2']
  
  d['filter'] = {} if not 'filter' in d else d['filter']
  d['filter2'] = {} if not 'filter2' in d else d['filter2']

  data = {}
  data['name'] = d['name']
  data['type'] = "DASHBOARD"
  data['sharing'] = "SYSTEM"

  columnLeft = { "width": "6", "rows": [{"panels": []}]}
  columnRight = { "width": "6", "rows": [{"panels": []}]}

  if (not d['title2']):
    column = columnLeft
    for index, row in df.iterrows():
      d['filter']['relApplicationToOwningUserGroup'] = row['id']
      column["rows"][0]["panels"].append(getPanel(d['filter'], row['name'] + " - " + d['title'], d['type'], d['tagGroupId'], d['singleSelectField']))
      if (column == columnLeft):
        column = columnRight
      else:
        column = columnLeft
  else: 
    for index, row in df.iterrows():
      d['filter']['relApplicationToOwningUserGroup'] = row['id']
      columnLeft["rows"][0]["panels"].append(getPanel(d['filter'], row['name'] + " - " + d['title'], d['type'], d['tagGroupId'], d['singleSelectField']))
      d['filter2']['relApplicationToOwningUserGroup'] = row['id']
      columnRight["rows"][0]["panels"].append(getPanel(d['filter2'], row['name'] + " - " + d['title2'], d['type2'], d['tagGroupId2'], d['singleSelectField2']))
          

  data["state"] = {
    "config": 
      {"rows": 
        [{"columns": 
          [columnLeft, columnRight]
        }]
      }
    }

  json_data = json.dumps(data)
  response = requests.post(url=request_url, headers=header, data=json_data)

  response.raise_for_status()
  print response.json()



