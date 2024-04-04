import json 
import requests 
import pandas as pd


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

    if choice == "10":
        request_url = 'https://demo-' + instance + '-1.leanix.net/services/pathfinder/v1/graphql'
    else:
        request_url = 'https://' + instance + '.leanix.net/services/pathfinder/v1/graphql'

except NameError:
    print("")
    print("Invalid input. Please enter a number.")
    print("")
    exit()


# Get the bearer token - see https://dev.leanix.net/v4.0/docs/authentication
response = requests.post(auth_url, auth=('apitoken', api_token),
                         data={'grant_type': 'client_credentials'})
response.raise_for_status() 
access_token = response.json()['access_token']
auth_header = 'Bearer ' + access_token
header = {'Authorization': auth_header}

# General function to call GraphQL given a query
def call(query):
  data = {"query" : query}
  json_data = json.dumps(data)
  print(json_data)
  response = requests.post(url=request_url, headers=header, data=json_data)
  response.raise_for_status()
  return response.json()

# Function to create an application via GraphQL
def createApplication(name):
  query = """
    mutation {
    createFactSheet(input: {name: "%s", type: Application}) {
      factSheet {
        id
      }
    }
  }
  """ % (name)
  print("Create Application " + name)
  response = call(query)
  return response['data']['createFactSheet']['factSheet']['id'] 

# Function to create an IT Component via GraphQL
def createITComponent(name):
  query = """
    mutation {
    createFactSheet(input: {name: "%s", type: ITComponent}) {
      factSheet {
        id
      }
    }
  }
  """ % (name)
  print("Create IT Component " + name)
  response = call(query)
  return response['data']['createFactSheet']['factSheet']['id'] 

# Function to create a relation between Application and IT Component with the costs attribute
def createRelationWithCosts(app, itc, costs) :
  query = """
    mutation {
      updateFactSheet(id: "%s", 
                      patches: [{op: add, path: "/relITComponentToApplication/new_1", value: "{\\\"factSheetId\\\": \\\"%s\\\",\\\"costTotalAnnual\\\": %s}"}]) {
        factSheet {
          id
        } 
      }
    }
  """ % (itc, app, costs)
  print("Create relation with costs: " + itc + "->" + app + " = " + str(costs))
  call(query)

# Start of the main logic

# 1. Read the input as a CSV
df = pd.read_csv('example.csv')

# 2. Make sure to create all applications, and save the created ids
apps = {}
for appName in df.loc[:, "app"].unique():
  apps[appName] = createApplication(appName)

# 3. Make sure to create all IT Components, and save the created ids
itcs = {}
for itcName in df.loc[:, "itc"].unique():
  itcs[itcName] = createITComponent(itcName)

# 4. Create the relations based on the saved ids
for index, row in df.iterrows():
  createRelationWithCosts(apps[row['app']], itcs[row['itc']], row['costs'])
