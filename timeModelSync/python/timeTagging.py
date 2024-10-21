import json
import queries # this is the queries.py file, located in the same subfolder
import requests
import os
import logging


logging.basicConfig(level=logging.INFO)

#Request timeout
TIMEOUT = 20

#API token and subdomain set as env variables
LEANIX_API_TOKEN = os.getenv('LEANIX_API_TOKEN')
LEANIX_SUBDOMAIN = os.getenv('LEANIX_SUBDOMAIN')

LEANIX_AUTH_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net/services/mtm/v1/oauth2/token' 
LEANIX_REQUEST_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net/services/pathfinder/v1/graphql'


#INPUT
mtm_base_url = LEANIX_AUTH_URL
pathfinder_base_url = LEANIX_REQUEST_URL
api_token = LEANIX_API_TOKEN


#Authorization
def getAccessToken(api_token):
  #different than callPost since it needs to send the auth_header
  response = requests.post(mtm_base_url+"/oauth2/token", auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'}, timeout=TIMEOUT)
  response.raise_for_status() 
  access_token = response.json()['access_token']
  return access_token


def getHeader(access_token):
  return {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}


# General function to call GraphQL given a query
def callGraphQL(query, access_token):
  #print("callGraphQl")
  data = {"query" : query}
  json_data = json.dumps(data)
  #print("request")
  response = requests.post(url=pathfinder_base_url + '/graphql', headers=getHeader(access_token), data=json_data, timeout=TIMEOUT)
  response.raise_for_status()
  #print("requested")
  return response.json()


def call(url, access_token):
  response = requests.get(url=pathfinder_base_url + '/' + url, headers=getHeader(access_token), timeout=TIMEOUT)
  response.raise_for_status()
  return response.json()


def getTimeTags():
    query = queries.getTimeTagsQuery()
    status, result = callGraphQL(query, getAccessToken(api_token))
    if not (status == 200 and result['errors'] is None):
        logging.error("Error in mapping the Time Model tags.")
        exit(9)
    tagMapping = {}
    for tagNode in result['data']['allTags']['edges']:
        tag = tagNode['node']
        tagMapping[tag['name']]=tag['id']
    return tagMapping

TIME_MAPPING = getTimeTags()

# This maps the various functional suitability fields to specific values
FUNCTIONAL_SUITABILITY_MAPPING = {"inappropriate": 1,
                                  "unreasonable": 2,
                                  "adequate": 3,
                                  "fullyAppropriate": 4}

# This maps the various technical suitability fields to specific values
TECHNICAL_SUITABILITY_MAPPING = {"unreasonable": 1,
                                 "insufficient": 2,
                                 "appropriate": 3,
                                 "perfect": 4}

"""
Logic:
1) Applications with Functional Fit 1/2 and Technical Fit 3/4 should be tagged with Migrate
2) Applications with Functional Fit 3/4 and Technical Fit 3/4 should be tagged with Invest
3) Applications with Functional Fit 3/4 and Technical Fit 1/2 should be tagged with Tolerate
4) Applications with Functional Fit 1/2 and Technical Fit 1/2 should be tagged with Eliminate
"""
## Function calculates the required Time tag, depending on the functionalFit and technicalFit
def calculateTimeTag(functionalSuitability, technicalSuitability):
    if functionalSuitability is None or technicalSuitability is None:
        return None
    elif FUNCTIONAL_SUITABILITY_MAPPING[functionalSuitability] >= 3 and TECHNICAL_SUITABILITY_MAPPING[technicalSuitability] <= 2:
        return TIME_MAPPING["Tolerate"]
    elif FUNCTIONAL_SUITABILITY_MAPPING[functionalSuitability] >= 3 and TECHNICAL_SUITABILITY_MAPPING[technicalSuitability] >= 3:
        return TIME_MAPPING["Invest"]
    elif FUNCTIONAL_SUITABILITY_MAPPING[functionalSuitability] <= 2 and TECHNICAL_SUITABILITY_MAPPING[technicalSuitability] >= 3:
        return TIME_MAPPING["Migrate"]
    elif FUNCTIONAL_SUITABILITY_MAPPING[functionalSuitability] <= 2 and TECHNICAL_SUITABILITY_MAPPING[technicalSuitability] <= 2:
        return TIME_MAPPING["Eliminate"]

## Function to filter out all existing tags that are not part of the Time tag-group
def getTagPatchesValues(tags, timeTag):
    newTags = [{"tagId": timeTag}]
    for tag in tags:
        if tag["tagId"] not in TIME_MAPPING.values():
            newTags.append(tag)
    escapedTagString = json.dumps(newTags).replace('"','\"')
    return escapedTagString

## Wrapper function to fetch all applications and their existing tags
def getAllApplications():
    query = queries.getFetchAllApplicationsQuery()
    return callGraphQL(query, getAccessToken(api_token))

## Wrapper function to update a specific revision of a factsheet
def updateApplication(id, rev, tagPatches):
    query = queries.getUpdateTagQuery(id,rev,tagPatches)
    return callGraphQL(query, getAccessToken(api_token))


## Start of Main Application
status, allApplications = getAllApplications()

#cycles through all applications
for appNode in allApplications['data']['allFactSheets']['edges']:
    application = appNode['node']

    tag = calculateTimeTag(
        application["technicalSuitability"], application["functionalSuitability"])
    if tag is not None:
        status, results = updateApplication(
            application['id'], application['rev'], getTagPatchesValues(application["tags"], tag))
        if results["errors"] is None:
            results['data']['result']
            logging.info(status, " - ", json.dumps(results['data']['result']))
