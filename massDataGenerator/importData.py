import json
import string

import requests
import pandas as pd
import random
import uuid
import click

api_token = '<API-Token>'
auth_url = 'https://<URL>/services/mtm/v1/oauth2/token'
request_url = 'https://<URL>/services/integration-api/v1/'

amount_BusinessCapabilities = 10
amount_Applications = 20
appList = []
bcList = []

# Get the bearer token - see https://dev.leanix.net/v4.0/docs/authentication
response = requests.post(auth_url, auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'})
response.raise_for_status()
header = {'Authorization': 'Bearer ' + response.json()['access_token'], 'Content-Type': 'application/json'}


def createRun(customFields, content):
    data = {
        "connectorType": "massData",
        "connectorId": "randomImport",
        "connectorVersion": "0.1",
        "lxVersion": "1.0.0",
        "description": "Imports massData into LeanIX",
        "processingDirection": "inbound",
        "processingMode": "partial",
        "customFields": customFields,
        "content": content
    }

    print(data)
    response = requests.post(url=request_url + 'synchronizationRuns/', headers=header, data=json.dumps(data))
    print(response.json())
    return (response.json())


def startRun(run):
    response = requests.post(url=request_url + 'synchronizationRuns/' + run['id'] + '/start?test=false', headers=header)


def status(run):
    response = requests.get(url=request_url + 'synchronizationRuns/' + run['id'] + '/status', headers=header)
    return (response.json())


def getResults(run):
    response = requests.get(url=request_url + 'synchronizationRuns/' + run['id'] + '/results', headers=header)

    if response.status_code == 204:
        print("No result content available for run: " + run['id'])
    else:
        return (response.json())


def relationProcessor(fsType, rel):
    return {
        "processorType": "inboundRelation",
        "processorName": "Rel from Apps to ITComponent",
        "processorDescription": "My description",
        "filter": {
            "type": fsType
        },
        "run": 1,
        "type": rel,
        "from": {
            "external": {
                "type": "externalId",
                "id": "${content.id}"
            }
        },
        "to": {
            "external": {
                "type": "externalId",
                "id": "${data.itc}"
            }
        }
    }


def randomBusinessCapabilityName(length):
    """Generate a random string of fixed length """
    letters = string.ascii_letters + " "
    randomName = ''.join(random.choice(letters) for i in range(length))
    return randomName


def createBusinessCapability(countBc):
    bcUuid = []
    bcRandom = []
    bcLevel = []

    j = 1
    while j <= countBc:
        bcRandom.append(randomBusinessCapabilityName(random.randint(2, 100)))
        bcUuid.append(str(uuid.uuid4()))
        bcLevel.append(random.randint(1, 5))
        j = j + 1

    data = {'bcUuid': bcUuid, 'bcName': bcRandom, 'bcLevel': bcLevel}
    return pd.DataFrame(data)


def printBusinessCapabilityJson(bcDf):
    businessCapabilities = []
    for index, row in bcDf.iterrows():
        if row['bcLevel'] == 1:
            businessCapabilities.append({
                "type": "BusinessCapability",
                "id": row['bcUuid'],
                "data": {"name": row['bcName'], "level": row['bcLevel'], "parent": "null"}
            })
        elif row['bcLevel'] == 2:
            parent = bcDf[bcDf['bcLevel'] == 1].sample(1)
            businessCapabilities.append({
                "type": "BusinessCapability",
                "id": row['bcUuid'],
                "data": {"name": row['bcName'], "level": row['bcLevel'], "parent": parent['bcUuid'].to_string(index=False).strip()}
            })
        elif row['bcLevel'] == 3:
            parent = bcDf[bcDf['bcLevel'] == 2].sample(1)
            businessCapabilities.append({
                "type": "BusinessCapability",
                "id": row['bcUuid'],
                "data": {"name": row['bcName'], "level": row['bcLevel'], "parent": parent['bcUuid'].to_string(index=False).strip()}
            })
        elif row['bcLevel'] == 4:
            parent = bcDf[bcDf['bcLevel'] == 3].sample(1)
            businessCapabilities.append({
                "type": "BusinessCapability",
                "id": row['bcUuid'],
                "data": {"name": row['bcName'], "level": row['bcLevel'], "parent": parent['bcUuid'].to_string(index=False).strip()}
            })
        elif row['bcLevel'] == 5:
            parent = bcDf[bcDf['bcLevel'] == 4].sample(1)
            businessCapabilities.append({
                "type": "BusinessCapability",
                "id": row['bcUuid'],
                "data": {"name": row['bcName'], "level": row['bcLevel'], "parent": parent['bcUuid'].to_string(index=False).strip()}
            })

    return businessCapabilities


def randomApplicationName(length):
    """Generate a random string of fixed length """
    randomSuffix = random.randint(0,10)
    suffixLetters = "." + "-" + "/"
    letters = string.ascii_letters + " "
    output = ''.join(random.choice(letters) for i in range(length))
    if randomSuffix < 5 and len(output) < 97:
        suffix = ''.join(random.choice(suffixLetters) for i in range(3))
        output = output + suffix
    return output


def createApplication(countBc, countApp):
    appUuid = []
    appRandom = []
    appBcRel = []

    list = generate_random_integers(countApp, countBc)
    bcUuidList = bcList['bcUuid']

    check = sum(list)

    c = 0
    for x in list:
        for y in range(x):
            appBcRel.append(bcUuidList[c])
        c = c + 1

    j = 1
    while j <= countApp:
        appRandom.append(randomApplicationName(random.randint(2, 100)))
        appUuid.append(str(uuid.uuid4()))
        j = j + 1

    data = {'appUuid': appUuid, 'appName': appRandom, 'clusterName': appBcRel}
    return pd.DataFrame(data)


def printApplicationJson(appDf):
    applications = []
    for index, row in appDf.iterrows():
        applications.append({
            "type": "Application",
            "id": row['appUuid'],
            "data": {"name": row['appName'], "clusterName": row['clusterName']}
        })
    return applications


def generate_random_integers(_sum, n):
    mean = round(_sum / n)
    variance = int(0.99 * mean)

    min_v = mean - variance
    max_v = mean + variance
    array = [min_v] * n

    diff = _sum - min_v * n
    while diff > 0:
        a = random.randint(0, n - 1)
        if array[a] >= max_v:
            continue
        array[a] += 1
        diff -= 1
    return array



# 1. Create random BusinessCapabilities (4.000, name 2-100 char and 0-3 spaces, 1-5 levels) > configurable
bcList = createBusinessCapability(amount_BusinessCapabilities)

# 2. Create random Applications (50.000, name 2-100 char and 0-3 spaces, sometimes suffix 1-5 char incl. ".","-","/")
appList = createApplication(amount_BusinessCapabilities, amount_Applications)

# 3. Print and merge Json
bcJson = printBusinessCapabilityJson(bcList)
appJson = printApplicationJson(appList)
content = bcJson + appJson
customFields = {}

# 4. Run script
run = createRun(customFields, content)
startRun(run)
while (True):
    if (status(run)['status'] == 'FINISHED'): break

