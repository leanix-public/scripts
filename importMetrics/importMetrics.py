import requests 
import csv
import os
import logging


logging.basicConfig(level=logging.INFO)

#Request timeout
TIMEOUT = 20

#API token and subdomain set as env variables
LEANIX_API_TOKEN = os.getenv('LEANIX_API_TOKEN')
LEANIX_SUBDOMAIN = os.getenv('LEANIX_SUBDOMAIN')

LEANIX_AUTH_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net/services/mtm/v1/oauth2/token' 
LEANIX_REQUEST_URL = f'https://{LEANIX_SUBDOMAIN}.leanix.net/services/metrics/v2'

IMPORT_FILE = os.getenv('IMPORT_FILE')
 

#LOGIC
# Get the bearer token - see https://dev.leanix.net/v4.0/docs/authentication
def get_bearer_token(auth_url, api_token):
    """Function to retrieve the bearer token for authentication

    Args:
        auth_url (str): URL to retrieve the bearer token from
        api_token (str): The api-token to authenticate with

    Returns:
        dict: Dictionary containing the bearer token
    """
    if not LEANIX_API_TOKEN:
        raise Exception('A valid token is required')
    response = requests.post(auth_url, auth=('apitoken', api_token),
                             data={'grant_type': 'client_credentials'},
                             timeout=TIMEOUT)
    response.raise_for_status() 
    access_token = response.json()['access_token']
    auth_header = 'Bearer ' + access_token
    header = {'Authorization': auth_header}
    return header

try:
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, IMPORT_FILE)
except ValueError:
    logging.error('Failed to parse file input')
        
try:
    header = get_bearer_token(LEANIX_AUTH_URL, LEANIX_API_TOKEN)
except Exception as e:
    logging.error(f'Error while authenticating: {e}')


with open(filename) as df:
    try:
        logging.info(f'Parsing csv file: {df.name}')
        reader = csv.DictReader(df, delimiter=';')
    except Exception as e:
        logging.error(f'Failed to load csv file: {e}')

    data = [row for row in reader]

    schema_name = data[0]["measurement"]

    keys = [] 
    for row in data:
        keys.append(row["key"])

    keys = [key for key in keys (dict.fromkeys(keys))]
    attributes = [{"name": key, "type": "metric"} for key in keys] + [{"name": "factSheetId", "type": "dimension"}]

    schema = {
      "name": schema_name,
      "description": "Daily costs for cloud resources.",
      "attributes": attributes
    }
    response = requests.post(url=f"{LEANIX_REQUEST_URL}/schemas", headers=header, json=schema, timeout=TIMEOUT)
    schema_uuid = response.json()["uuid"]

    for row in data:
      data = {
          "timestamp": row['date'].strftime('%Y-%m-%d') + "T00:00:00.000Z",
          "factSheetId": row["factSheetId"],
          row['key']: row['value']
        }
      response = requests.post(url=f"{LEANIX_REQUEST_URL}/schemas/{schema_uuid}/points", headers=header, json=data, timeout=TIMEOUT)

      response.raise_for_status()
      logging.info(response.json())
