def getFetchAllApplicationsQuery():
    query = {"query": """{
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
    return query


def getUpdateTagQuery(id, rev, tagPatches):
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
    return query
