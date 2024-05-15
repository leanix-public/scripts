import json 
import requests 
import csv
import os
import logging


logging.basicConfig(level=logging.INFO)

#Request timeout
TIMEOUT = 20

#API token and subdomain set as env variables
LEANIX_API_TOKEN = os.getenv('LEANIX_API_TOKEN')
LEANIX_SUBDOMAIN = os.getenv('LEANIX_SUBDOMAIN')

LEANIX_AUTH_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net/services/mtm/v1/oauth2/token' 
LEANIX_REQUEST_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net/services/pathfinder/v1/bookmarks'

IMPORT_FILE = os.getenv('IMPORT_FILE')


#LOGIC
# Get the bearer token - see https://dev.leanix.net/v4.0/docs/authentication
def get_bearer_token(auth_url, api_token):
    """Function to retrieve the bearer token for authentication

    Args:
        auth_url (str): URL to retrieve the bearer token from
        api_token (str): The api-token to authenticate with

    Returns:
        dict: Dictionary containing the bearer token
    """
    if not LEANIX_API_TOKEN:
        raise Exception('A valid token is required')
    response = requests.post(auth_url, auth=('apitoken', api_token),
                             data={'grant_type': 'client_credentials'},
                             timeout=TIMEOUT)
    response.raise_for_status() 
    access_token = response.json()['access_token']
    auth_header = 'Bearer ' + access_token
    header = {'Authorization': auth_header}
    return header
  

def getPanel(filters, title, chartType, tagGroupId, singleSelectField):
    """Retrieves the panel

    Args:
        filters (_type_): _description_
        title (_type_): _description_
        chartType (_type_): _description_
        tagGroupId (_type_): _description_
        singleSelectField (_type_): _description_

    Returns:
        _type_: _description_
    """  
    panel1 = {}
    panel1["title"] = title
    panel1["type"] = "CHART"
    panel1["options"] = {"chartType": chartType, "tagGroupId": tagGroupId, "singleSelectField": singleSelectField, "filter":  getFilter(filters) }
    return panel1


def getFilter(filters):
    """_summary_

    Args:
        filters (_type_): _description_

    Returns:
        _type_: _description_
    """  
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


try:
    with open('input.csv') as df:
        try:
            logging.info(f'Parsing csv file: {df.name}')
            reader = csv.DictReader(df, delimiter=';')

        except Exception as e:
            logging.error(f'Failed to load csv file: {e}')

    file_name = './dashboards.json'
    with open(file_name, 'r') as f:
        dashboards = json.load(f)

except Exception as e:
   logging.error(f'Failed to load input file: {e}')


try:
    header = get_bearer_token(LEANIX_AUTH_URL, LEANIX_API_TOKEN)
except Exception as e:
    logging.error(f'Error while authenticating: {e}')

for d in dashboards:
  d['singleSelectField'] = '' if 'singleSelectField' not in d else d['singleSelectField']
  d['singleSelectField2'] = '' if 'singleSelectField2' not in d else d['singleSelectField2']
 
  d['tagGroupId'] = '' if 'tagGroupId' not in d else d['tagGroupId']
  d['tagGroupId2'] = '' if 'tagGroupId2' not in d else d['tagGroupId2']
  d['title2'] = '' if 'title2' not in d else d['title2']
  
  d['filter'] = {} if 'filter' not in d else d['filter']
  d['filter2'] = {} if 'filter2' not in d else d['filter2']

  data = {}
  data['name'] = d['name']
  data['type'] = "DASHBOARD"
  data['sharing'] = "SYSTEM"

  columnLeft = { "width": "6", "rows": [{"panels": []}]}
  columnRight = { "width": "6", "rows": [{"panels": []}]}

  if (not d['title2']):
    column = columnLeft
    for row in reader:
      d['filter']['relApplicationToOwningUserGroup'] = row['id']
      column["rows"][0]["panels"].append(getPanel(d['filter'], row['name'] + " - " + d['title'], d['type'], d['tagGroupId'], d['singleSelectField']))
      if (column == columnLeft):
        column = columnRight
      else:
        column = columnLeft
  else: 
    for row in reader:
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
  response = requests.post(url=LEANIX_REQUEST_URL, headers=header, data=json_data, timeout=TIMEOUT)
  response.raise_for_status()

  logging.info(response.json())
