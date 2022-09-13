import json
import requests
import getopt, sys

auth_url = 'https://de-svc.leanix.net/services/mtm/v1/oauth2/token'
discovery_api_url = 'https://demo-de.leanix.net/services/vsm-collector/v1/item'
graphql_url = "https://demo-de.leanix.net/services/pathfinder/v1/graphql"

argumentList = sys.argv[1:]

# Short args
short_args = "ho:n:"

# Long args
long_args = ["--help", "oldvsm_apitoken=", "newvsm_apitoken="]

#Read tokens from stdin
try:
	arguments, values = getopt.getopt(argumentList, short_args, long_args)

	for currentArgument, currentValue in arguments:
		if currentArgument in ("-h", "--help"):
			print ("Usage: " + sys.argv[0] + " [args]\n" + "-o | --oldvsm_apitoken    Technical user token from old VSM \n" + "-n | --newvsm_apitoken    Technical user token from new VSM \n")
			sys.exit()
		elif currentArgument in ("-o", "--oldvsm_apitoken"):
			oldvsm_apitoken = currentValue
		elif currentArgument in ("-n", "--newvsm_apitoken"):
			newvsm_apitoken = currentValue
except getopt.error as err:
	print ("Usage: " + sys.argv[0] + " [args]\n" + "-o | --oldvsm_apitoken    Technical user token from old VSM \n" + "-n | --newvsm_apitoken    Technical user token from new VSM \n")
	sys.exit(1)

#Check if both tokens are provided
try:
    oldvsm_apitoken
    newvsm_apitoken
except NameError as error:
    print("\n" + str(error).split("'")[1] + " is not provided\n")
    print ("Usage: " + sys.argv[0] + " [args]\n" + "-o | --oldvsm_apitoken    Technical user token from old VSM \n" + "-n | --newvsm_apitoken    Technical user token from new VSM \n")
    sys.exit(1)

# function to call graphQL in old VSM
def getGraphQl(query, access_token):
    response = callPost(graphql_url, access_token, query)
    return response

# A simple graphql query to get all Software Artifact factsheets with some core fields
def getAllFactsheetsQuery():
    query = """
  {
  allFactSheets(factSheetType: Microservice) {
    edges {
      node {
        name
        description
        id
        type
      }
    }
  }
}
  """
    return {"query": query}

def getAccessToken(api_token):
    response = requests.post(auth_url, auth=('apitoken', api_token),
                             data={'grant_type': 'client_credentials'})
    response.raise_for_status()
    access_token = response.json()['access_token']
    return access_token


def callGet(request_url, access_token):
    response = requests.get(url=request_url, headers={
                            'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'})
    response.raise_for_status()
    return response.json()


def callPost(request_url, access_token, data):
    try:
        response = requests.post(url=request_url, headers={
                                 'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}, json=data)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(request_url)
        print(json.dumps(data))
        print(err)
        exit
    return response


def getServiceData(serviceId, name, description):
    data = {
        "type": "SERVICE",
        "id": serviceId,
        "sourceType": "monolith",  # Category of the service
        "sourceInstance": "manual",  # location,domain or any identifier can be used
        "name": name,
        "description": description,
        "data": {  # the data contained here must be purely string objects
        }
    }

    return data


# Must authenticate to the old vsm
old_vsm_token = getAccessToken(oldvsm_apitoken)
#print(f"Old VSM Token used: {old_vsm_token}\n")

# Must authenticate to the new vsm
new_vsm_token = getAccessToken(newvsm_apitoken)
#print(f"new VSM Token: {new_vsm_token}\n")

# Export all the Software Artifact factsheets from the old vsm via graphql
response = getGraphQl(getAllFactsheetsQuery(), old_vsm_token)
#print(
#    f"response code: {response.status_code}\nresponse size: {len(response.text)}")

# Extract the factsheets from the response of the graphql request
edges = response.json().get('data').get('allFactSheets').get('edges')

# For the id of the service, an auto-increment number is fine
incr_service_id = 1

# Loop over the factsheets
for edge in edges:
    # Data is actually stored on the "node", not the "edge"
    node = edge.get("node")

    # Convert the data from old vsm into a json format for the api
    service_data = getServiceData(
        f'{incr_service_id:04}', node.get("name"), node.get("description"))

    print(service_data)

    # Upload the service to the new vsm
    status = callPost(discovery_api_url, new_vsm_token, service_data)

    # Increment the id for the next item
    incr_service_id += 1
