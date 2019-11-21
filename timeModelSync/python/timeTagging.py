import json
import lxpy # this is the leanix-python-client and requires a 'pip install leanix_python_client-0.2.0-py3-none-any.whl'
import queries # this is the queries.py file, located in the same subfolder
from os import environ

config = lxpy.ClientConfiguration(
    base_url=environ.get('BASE_URL', 'customer.leanix.net'),
    api_token=environ.get('API_TOKEN', 'my-api-token')
)

pathfinder = lxpy.Pathfinder(config)

def getTimeTags():
    query = queries.getTimeTagsQuery()
    status, result = pathfinder.post("/graphql",query)
    if not (status == 200 and result['errors'] is None):
        print("Error in mapping the Time Model tags.")
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
    return pathfinder.post("/graphql", query)

## Wrapper function to update a specific revision of a factsheet
def updateApplication(id, rev, tagPatches):
    query = queries.getUpdateTagQuery(id,rev,tagPatches)
    return pathfinder.post("/graphql", query)


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
            print(status, " - ", json.dumps(results['data']['result']))