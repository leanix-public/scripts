import logging
import json
import lxpy
from os import environ
import azure.functions as func

config = lxpy.ClientConfiguration(
    base_url= environ['HOST'],
    api_token= environ['DEMO_TOKEN']
)

pathfinder = lxpy.Pathfinder(config)

def getApplication(fsId):
    getQuery = {"query": """{
    factSheet(id: "%s") {
        id
        rev
        ... on Application {
        technicalSuitability
        functionalSuitability
        }
        tags {
        tagId: id
        }
    }
    }""" %(fsId)}
    status, results = pathfinder.post("/graphql", getQuery)
    return results


FUNCTIONAL_SUITABILITY_MAPPING = {"inappropriate": 1,
                                  "unreasonable": 2,
                                  "adequate": 3,
                                  "fullyAppropriate": 4}

TECHNICAL_SUITABILITY_MAPPING = {"unreasonable": 1,
                                 "insufficient": 2,
                                 "appropriate": 3,
                                 "perfect": 4}

TIME_MAPPING = environ['TAG_MAPPING']

def calculateTimeTag(functionalSuitability, technicalSuitability):
    if functionalSuitability is None or technicalSuitability is None:
        return None
    elif FUNCTIONAL_SUITABILITY_MAPPING[functionalSuitability] >= 3 and TECHNICAL_SUITABILITY_MAPPING[technicalSuitability] >= 3:
        return TIME_MAPPING["invest"]
    elif FUNCTIONAL_SUITABILITY_MAPPING[functionalSuitability] <= 2 and TECHNICAL_SUITABILITY_MAPPING[technicalSuitability] >= 3:
        return TIME_MAPPING["tolerate"]
    elif FUNCTIONAL_SUITABILITY_MAPPING[functionalSuitability] <= 2 and TECHNICAL_SUITABILITY_MAPPING[technicalSuitability] <= 2:
        return TIME_MAPPING["eliminate"]
    elif FUNCTIONAL_SUITABILITY_MAPPING[functionalSuitabiliçty] >= 3 and TECHNICAL_SUITABILITY_MAPPING[technicalSuitability] <= 2:
        return TIME_MAPPING["migrate"]

def getTagPatchesValues(tags, timeTag):
    newTags = [{"tagId": timeTag}]
    for tag in tags:
        if tag["tagId"] not in TIME_MAPPING.values():
            newTags.append(tag)
    escapedTagString = json.dumps(newTags).replace('"','\"')
    return escapedTagString

def updateApplication(id, rev, tagPatches):
    query = {"query": """
    mutation($patches:[Patch]!){result:updateFactSheet(id:\"%s\", rev:%d, patches:$patches, validateOnly:false){factSheet{...on Application{displayName tags{name tagGroup{name}}}}}}
    """ % (id, rev),
        "variables": {
        "patches": [
            {
                "op": "replace",
                "path": "/tags",
                "value": tagPatches
            }
        ]
    }
    }
    status, result = pathfinder.post("/graphql", query)
    return result


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    try:
        req_body = req.get_json()
        application = getApplication(req_body['factSheet']['id'])['data']['factSheet']
        logging.info(application)
    except ValueError:
        pass
    tag = calculateTimeTag(
        application["technicalSuitability"], application["functionalSuitability"])
    if tag is not None:
        response = (json.dumps(updateApplication(
            application['id'], application['rev'], getTagPatchesValues(application["tags"], tag))))
        logging.info(response)
        return func.HttpResponse(response)

