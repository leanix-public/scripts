import json 
import requests 
import pandas as pd

api_token = '<api-token>'
workspaceId = '<workspace-id>'
auth_url = 'https://app.leanix.net/services/mtm/v1/oauth2/token' 
request_url = 'https://svc.leanix.net/services/pathfinder/v1/' 

# Authentication
response = requests.post(auth_url, auth=('apitoken', api_token), data={'grant_type': 'client_credentials'})
response.raise_for_status()
access_token = response.json()['access_token']
auth_header = 'Bearer ' + access_token
header = {'Authorization': auth_header}

def generateExport():
# generate full export
  print (header)
  print ("executing request")
  export_url = request_url +  "exports/fullExport?exportType=SNAPSHOT"
  print("ExportURL = "+export_url)
  response = requests.post(url=export_url, headers=header)
  response.raise_for_status()
  return response.json()

def getDocumentId():
  document_url = request_url + "exports?exportType=SNAPSHOT&pageSize=1&sorting=createdAt&sortDirection=DESC"
  print("documentURL = "+document_url)
  response = requests.get(url=document_url, headers=header)
  response.raise_for_status()
  responseJson = response.json()
  print(responseJson)
  return responseJson['data'][0]['downloadKey']

def downloadDocument(downloadKey, exportFile):
  download_url = request_url + "exports/downloads/"+workspaceId+"?key="+downloadKey
  print("DownloadURL = "+download_url)
  response = requests.get(url=download_url, headers=header )
  response.raise_for_status()
  with open(exportFile,'wb') as code:
    code.write(response.content)
  return

getDocumentId()
#downloadDocument(getDocumentId(),'export.xlsx')

