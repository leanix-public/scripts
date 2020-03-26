import json
import requests
import sys
import base64
import click
import pandas as pd

# Define Global variables here
# Required Global Variable : apiToken
apiToken = ""
# Update the externalUrl with the ServiceInstance Name and tableName
externalUrl = "https://<ServiceInstance>.service-now.com/nav_to.do?uri=<tableName>.do?sys_id="
base_url = 'https://app.leanix.net'

def getAccessToken(api_token):
    api_token = api_token
    auth_url = base_url+'/services/mtm/v1/oauth2/token'

    # Get the bearer token - see https://dev.leanix.net/v4.0/docs/authentication
    response = requests.post(auth_url, auth=('apitoken', api_token),
                             data={'grant_type': 'client_credentials'})
    response.raise_for_status()
    access_token = response.json()['access_token']
    return access_token

# Function to decipher the access_token
def getAccessTokenJson(access_token):
    payload_part = access_token.split('.')[1]
    # fix missing padding for this base64 encoded string.
    # If number of bytes is not dividable by 4, append '=' until it is.
    missing_padding = len(payload_part) % 4
    if missing_padding != 0:
        payload_part += '=' * (4 - missing_padding)
    payload = json.loads(base64.b64decode(payload_part))
    return payload

# runUpdate method to update ServiceNow ExternalId
def runUpdate(access_token):
    df = pd.read_csv('ServiceNow.csv', sep=';')
    for index, row in df.iterrows():
        runMutation(row['id'], access_token,row['serviceNowExternalId'])

def runMutation(factSheetId, access_token, serviceNowExternalId):
    status = "LINKED"
    serviceNowUrl = externalUrl+serviceNowExternalId
   # tags.append(tagId)
    #tags = list(dict.fromkeys(tags))
    #patches = ""
    #technopediaString = '{\\\"type\\\": \\\"ExternalId\\\",\\\"externalId\\\": \\\"'+ technopediaId +'\\\",\\\"comment\\\": \\\"This Fact Sheet was linked to an entry in Technopedia\\\",\\\"status\\\": \\\"LIFECYCLE_ONLY\\\"}'
    if(status == 'LINKED'):
        patches = "{op: replace, path: \"/serviceNowExternalId\", value: \"{\\\"type\\\": \\\"ExternalId\\\",\\\"externalId\\\": \\\""+ serviceNowExternalId +"\\\",\\\"externalVersion\\\": \\\"\\\",\\\"comment\\\": \\\"This Fact Sheet was linked to an entry in ServiceNow\\\",\\\"status\\\": \\\"LINKED\\\",\\\"externalUrl\\\": \\\""+ serviceNowUrl +"\\\",\\\"forceWrite\\\":true}\"}"
    query = """
    mutation{
        updateFactSheet(id: "%s",patches: [%s]) {
        factSheet {
        id
        }
        }
      }
    """ % (factSheetId, patches)
    response_mutation = call("query", query, access_token)
    print(response_mutation)

# General function to call GraphQL given a query
def call(request_type, query, access_token):
    auth_header = 'Bearer ' + access_token
    header = {'Authorization': auth_header}
    request_url = base_url+'/services/pathfinder/v1/graphql'
    data = {request_type: query}
    json_data = json.dumps(data)
    response = requests.post(url=request_url, headers=header, data=json_data)
    response.raise_for_status()
    return response.json()

# start of main program
if __name__ == '__main__':
    access_token = getAccessToken(apiToken)
    access_token_json = getAccessTokenJson(access_token)
    print(access_token_json['principal']['username'])
    print(access_token_json['principal']['permission']['workspaceName'])
    if click.confirm('Do you want to continue?', default=True):
      runUpdate(access_token)