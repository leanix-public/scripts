import json
import lxpy
from os import environ

# Search User Base for a certain subscription role and adjust their Authorization level accordingly

config = lxpy.ClientConfiguration(
    base_url=environ.get('BASE_URL', 'customer.leanix.net'),
    api_token=environ.get('API_TOKEN', 'my-api-token')
)

pathfinder = lxpy.Pathfinder(config)

def getAllApplications():
  getQuery = {"query": """{
    allFactSheets(filter: {facetFilters: [{facetKey: "FactSheetTypes", operator: OR, keys: ["Application"]}]}) {
      edges {
        node {
          id
          rev
          ... on Application {
            technicalSuitability
            functionalSuitability
          }
          tags{
            tagId:id
          }
        }
      }
    }
  }"""}
  status, results = pathfinder.post("/graphql",getQuery)
  return results



# get Applications

"""
Hi Christoph, das Script wird doch erst einmal einfacher - Logik wäre:
1) Applikationen mit Functional Fit 3/4 und Technical Fit 3/4 erhalten das Tag Invest
2) Applikationen mit Functional Fit 1/2 und Technical Fit 3/4 erhalten das Tag Tolerate
3) Applikationen mit Functional Fit 1/2 und Technical Fit 1/2 erhalten das Tag Eliminate
4) Applikationen mit Functional Fit 3/4 und Technical Fit 1/2 erhalten das Tag Migrate
"""

TECHNICAL_SUITABILITY_MAPPING = {"inappropriate":1,
                        "unreasonable":2,
                        "adequate":3,
                        "fullyAppropriate":4}

FUNCTIONAL_SUITABILITY_MAPPING = {"unreasonable":1,
                         "insufficient":2,
                         "appropriate":3,
                         "perfect":4}

TIME_MAPPING = {
  "tolerate":"a69e7185-b7a4-438e-b3bb-cf54389444e5",
  "invest":"320c2f83-e1ec-4a1d-ad0e-06446490c66d",
  "migrate":"ee157b14-7710-4536-8360-ed9ff4acbd66",
  "eliminate":"08834c44-c123-45f2-88cb-ace29de0c894"
}

def calculateTimeTag(functionalSuitability,technicalSuitability):
  if functionalSuitability is None or technicalSuitability is None:
    return None
  elif FUNCTIONAL_SUITABILITY_MAPPING[functionalSuitability] >= 3 and TECHNICAL_SUITABILITY_MAPPING[technicalSuitability] >= 3:
    return TIME_MAPPING["invest"]
  elif FUNCTIONAL_SUITABILITY_MAPPING[functionalSuitability] <= 2 and TECHNICAL_SUITABILITY_MAPPING[technicalSuitability] >= 3:  
    return TIME_MAPPING["tolerate"]
  elif FUNCTIONAL_SUITABILITY_MAPPING[functionalSuitability] <= 2 and TECHNICAL_SUITABILITY_MAPPING[technicalSuitability] <= 2:
    return TIME_MAPPING["elimate"]
  elif FUNCTIONAL_SUITABILITY_MAPPING[functionalSuitability] >= 3 and TECHNICAL_SUITABILITY_MAPPING[technicalSuitability] <= 2:
   return TIME_MAPPING["migrate"]


def getTagPatchesValues(tags,timeTag):
  newTags = [{"tagId":timeTag}]
  for tagId in tags.values():
    if tagId not in TIME_MAPPING.values():
      newTags.append({"tagId":tagId})
  return newTags

#  [{\"tagId\":\"483cbd7c-1a8e-41c6-8312-7f629056b201\"},{\"tagId\":\"393b2ac2-413f-43ef-9c74-fc8f3400f040\"},{\"tagId\":\"5e8f21af-ebc6-4eca-a3e6-b71dbd89c958\"},{\"tagId\":\"ee157b14-7710-4536-8360-ed9ff4acbd66\"},{\"tagId\":\"2ddc9122-4513-40e2-afd8-4b28f41474a4\"},{\"tagId\":\"747a3871-c221-4bd9-9507-7acd0bdec421\"},{\"tagId\":\"320c2f83-e1ec-4a1d-ad0e-06446490c66d\"}]


def updateApplication(id, rev, tagPatches):
  query= {"query" : """mutation($patches:[Patch]!){result:updateFactSheet(id:\"%s\", rev:%d, patches:$patches, validateOnly:false)    factSheet {tags {name}}}"""%(id,rev),
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
  #print(json.dumps(query, indent=2))
  status, result = pathfinder.post("/graphql",query)
  return result

def updateApplication(app,timeTag):
#  if app
  query = {"query":"""mutation {
  updateFactSheet(id:"%s" patches:[{op: replace path: "/tags" value: "%s"}]) {
    factSheet {
      tags {
        name
      }
    }
  }
} 
  """
  ,
  "variables":""}
  status, result = pathfinder.post("/graphql",query)
  return result

allApplications = getAllApplications()

for appNode in allApplications['data']['allFactSheets']['edges']:
  application = appNode['node']
  tag = calculateTimeTag(application["technicalSuitibility"], application["functionalSuitibility"])
  if tag is not None:
    updateApplication(application['id'],application['rev'],getTagPatchesValues(application["tags"],tag))
    # update applicaton
