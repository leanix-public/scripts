import json 
import requests


"""
api_token = ''
auth_url = 'https://<mtm_region>.leanix.net/services/mtm/v1/oauth2/token' 
request_url = 'https://<customer_domain>.leanix.net/services/pathfinder/v1/graphql'
"""

#INPUT
auth_url = "Placeholder"
request_url = "Placeholder"

api_token = input("Enter your API-Token: ")

print("")
print("Choose the instance your workspace is on:")
print("")
print("1. EU")
print("2. US")
print("3. AU")
print("4. UK")
print("5. DE")
print("6. CH")
print("7. AE")
print("8. CA")
print("9. BR")
print(" ")

try:
    choice = input("Enter your choice (1/2/3/4/5/6/7/8/9): ")
           
    if choice == "1":
        instance = "eu"
    elif choice == "2":
        instance = "us"
    elif choice == "3":
        instance = "au"
    elif choice == "4":
        instance = "uk"
    elif choice == "5":
        instance = "de"
    elif choice == "6":
        instance = "ch"
    elif choice == "7":
        instance = "ae"
    elif choice == "8":
        instance = "ca"
    elif choice == "9":
        instance = "br"
    elif choice == "10":
        instance = "eu"
    else:
        print("")
        print("Invalid choice. Please select 1, 2, 3, 4, 5, 6, 7, 8 or 9")
        print("")

except ValueError:
    print("")
    print("Invalid input. Please enter a number.")
    print("")

try:
    auth_url = 'https://' + instance + '-svc.leanix.net/services/mtm/v1/oauth2/token' 

    if instance == 10:
        request_url = 'https://demo-' + instance + '-1.leanix.net/services/pathfinder/v1/graphql'
    else:
        request_url = 'https://' + instance + '.leanix.net/services/pathfinder/v1/graphql'

except NameError:
    print("")
    print("Invalid input. Please enter a number.")
    print("")
    exit()

"""
# Define fact sheet type, relationship name and constraining relationship name
factsheetType = 'Project'
relationship = 'relProjectToBusinessCapability'
constrainingRelationship = 'relProjectToUserGroup'
"""
        
try:
    factsheetType = input("Please enter the factsheet type: ")
except ValueError:
    print("")
    print("Invalid input.")
    print("")

try:
    relationship = input("Please enter the relationship: ")
except ValueError:
    print("")
    print("Invalid input.")
    print("")

try:
    constrainingRelationship = input("Please enter the constraining relationship: ")
except ValueError:
    print("")
    print("Invalid input.")
    print("")


response = requests.post(auth_url, auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'})
response.raise_for_status() 
access_token = response.json()['access_token']
auth_header = 'Bearer ' + access_token
header = {'Authorization': auth_header, 'Content-Type': 'application/json'}


# General function to call GraphQL given a query
def call(query):
  data = {"query" : query}
  json_data = json.dumps(data)
  response = requests.post(url=request_url, headers=header, data=json_data)
  return response.json()

def createConstraint(fs, constrainedType, constrainedId, constrainingType, constrainingId) :
  query = """
    mutation {
      createRelationConstraint(factSheetId: "%s", constrainedRelationType: "%s", constrainedRelationTargetFactSheetId: "%s", constrainingRelationType: "%s", constrainingRelationTargetFactSheetId: "%s")
      {  
       id
       name
      }
    }
  """ % (fs, constrainedType, constrainedId, constrainingType, constrainingId)
  print(call(query))

def fixConstraints(fsType='Project', rel='relProjectToBusinessCapability', constrainingRel='relProjectToUserGroup') :
  query = """
  { allFactSheets(factSheetType: %s) {
      edges { node { 
        id 
        name 
        ... on %s {
          %s {edges { node { factSheet { id name}}}}
          %s {edges { node { factSheet { id name}}}}
        }
      }}
  }}""" % (fsType, fsType, rel, constrainingRel)
  
  response = call(query)
  for fsNode in response['data']['allFactSheets']['edges']: # eg: Project
    fsId = fsNode['node']['id']
    fsName = fsNode['node']['name']
    for relFs in fsNode['node'][rel]['edges']: # eg: Business Capability
      relFsId = relFs['node']['factSheet']['id']
      relFsName = relFs['node']['factSheet']['name']
      for constrainRelFs in fsNode['node'][constrainingRel]['edges']: # eg: User Group
        constrainRelFsId = constrainRelFs['node']['factSheet']['id']
        constrainRelFsName = constrainRelFs['node']['factSheet']['name']
        print("""Creating constrinaning relation for '%s' between '%s' and '%s'""" %(fsName, relFsName, constrainRelFsName))
        createConstraint(fsId, rel, relFsId, constrainingRel, constrainRelFsId)
        
   
# Start of the main logic

fixConstraints(fsType=factsheetType, rel=relationship, constrainingRel=constrainingRelationship)
