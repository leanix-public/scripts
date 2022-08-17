import json 
import requests 
import pandas as pd

api_token = '<API-Token>'
ws_id = 'JEMDemo'
auth_url = 'https://app.leanix.net/services/mtm/v1/oauth2/token' 
request_url = 'https://app.leanix.net/services/metrics/v2' 

# Get the bearer token - see https://dev.leanix.net/v4.0/docs/authentication
response = requests.post(auth_url, auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'})
response.raise_for_status() 
access_token = response.json()['access_token']
auth_header = 'Bearer ' + access_token
header = {'Authorization': auth_header, 'Content-Type': 'application/json'}
  
df = pd.read_excel('input.xlsx', sheet_name='Worksheet')
schema_name = df["measurement"].tolist()[0]
keys = df["key"].unique().tolist()
attributes = [{"name": key, "type": "metric"} for key in keys] + [{"name": "factSheetId", "type": "dimension"}]
schema = {
  "name": schema_name,
  "description": "Daily costs for cloud resources.",
  "attributes": attributes
}
response = requests.post(url=f"{request_url}/schemas", headers=header, json=schema)
schema_uuid = response.json()["uuid"]
for index, row in df.iterrows():
  
  data = {
      "timestamp": row['date'].strftime('%Y-%m-%d') + "T00:00:00.000Z",
      "factSheetId": row["factSheetId"],
      row['key']: row['value']
    }
  response = requests.post(url=f"{request_url}/schemas/{schema_uuid}/points", headers=header, json=data)

  response.raise_for_status()
  print(response.json())



