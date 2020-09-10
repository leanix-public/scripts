from os import environ
import json
import requests
import pandas as pd

api_token = environ.get('LEANIX_API_TOKEN')
ws_id = 'MY_WORKSPACE_ID'
auth_url = 'https://app.leanix.net/services/mtm/v1/oauth2/token'
request_url = 'https://app.leanix.net/services/metrics/v1/points'

# Get the bearer token - see https://dev.leanix.net/v4.0/docs/authentication
response = requests.post(auth_url, auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'})
response.raise_for_status()
access_token = response.json()['access_token']
auth_header = 'Bearer ' + access_token
header = {'Authorization': auth_header, 'Content-Type': 'application/json'}

df = pd.read_excel('input.xlsx', sheet_name='Worksheet')

for index, row in df.iterrows():

    data = {
        "measurement": row['measurement'],
        "workspaceId": ws_id,
        "time": row['date'].strftime('%Y-%m-%d') + "T00:00:00.000Z",
        "tags": [
            {
                "k": "factSheetId",
                "v": row['factSheetId']
            }
        ],
        "fields": [
            {
                "k": row['key'],
                "v": row['value']
            }
        ]
    }
    json_data = json.dumps(data)
    response = requests.post(url=request_url, headers=header, data=json_data)

    response.raise_for_status()
    print(response.json())
