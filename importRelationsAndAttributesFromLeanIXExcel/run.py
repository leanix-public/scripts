import requests
import json
import time
import pandas as pd
import os
import numpy as np
import logging



non_match_records = []

with open('configs.json', 'r') as infile:
    configs = json.load(infile)
    date_fields = configs['date_fields']

#Request timeout
TIMEOUT = 20

#API token and subdomain set as env variables
LEANIX_API_TOKEN = os.getenv('LEANIX_API_TOKEN')
LEANIX_SUBDOMAIN = os.getenv('LEANIX_SUBDOMAIN')

IMPORT_FILE = os.getenv('IMPORT_FILE')

api_token = LEANIX_API_TOKEN
auth_url = f'https://{LEANIX_SUBDOMAIN}.leanix.net/services/mtm/v1/oauth2/token' 
request_base = f'https://{LEANIX_SUBDOMAIN}.leanix.net/'



response = requests.post(
    auth_url, auth=("apitoken", api_token), data={"grant_type": "client_credentials"},
    timeout=TIMEOUT
)

response.raise_for_status()
access_token = response.json()["access_token"]
auth_header = "Bearer " + access_token


header = {"Authorization": auth_header, "Content-Type": "application/json"}


def call_post(request_url, data=False):
    
    response = requests.post(
        url=request_url, headers=header, data=json.dumps(data), timeout=TIMEOUT
    )
    try:
        response.raise_for_status()
        return json.loads(response.text)
    except json.decoder.JSONDecodeError:
        pass


def call_put(request_url, data=False):
    
    response = requests.put(
        url=request_url, headers=header, data=json.dumps(data), timeout=TIMEOUT
    )
    try:
        response.raise_for_status()
        return json.loads(response.text)
    except json.decoder.JSONDecodeError:
        pass

def call_delete(request_url):
    response = requests.delete(
        url=request_url, headers=header, timeout=TIMEOUT)
    try:
        response.raise_for_status()
        return json.loads(response.text)
    except json.decoder.JSONDecodeError:
        pass



def call_get(request_url, endpoint):
    response = requests.get(url=request_url + endpoint, headers=header, timeout=TIMEOUT)
    response.raise_for_status()
    return response

def get_graphql(query):
    endpoint = request_base + 'services/pathfinder/v1/graphql'
    response = call_post(endpoint, query)
    return response

 
def create_run(run_config):
    create_run_endpoint = request_base + "services/integration-api/v1/synchronizationRuns"
    result = call_post(create_run_endpoint, run_config)
    return result['id']


def start_run(run_id):
    start_run_endpoint = request_base + "services/integration-api/v1/synchronizationRuns/%s/start" % (run_id)
    call_post(start_run_endpoint)


def check_run_status(run_id, status_response=None):
    logging.info("checking status")
    status_endpoint = request_base + "services/integration-api/v1/synchronizationRuns/%s/status" % (run_id)
    status_response = call_get(status_endpoint)
    status_response = json.loads(status_response.text)["status"]
    logging.info(status_response)
    if status_response != "FINISHED":
        time.sleep(5)
        return check_run_status(run_id, status_response)
    else:
        return True


def fetch_results(run_id):
    results_endpoint = request_base + "services/integration-api/v1/synchronizationRuns/%s/results" % (run_id)
    results_response = call_get(results_endpoint)
    return json.loads(results_response.text)


def handle_run(ldif_data, processing_direction):
    run_id = create_run(ldif_data)
    if start_run(run_id) == 200:
        if check_run_status(run_id) == True:
            if processing_direction == "outbound":
                return fetch_results(run_id)
            elif processing_direction == "inbound":
                return f"inbound run: {run_id} finished successfully"


def put_connector(connector_data):
    endpoint = request_base + "services/integration-api/v1/configurations"
    call_put(endpoint, connector_data)


def delete_connector(connector_data):
    endpoint = request_base + f"services/integration-api/v1/configurations?connectorType={connector_data['connectorType']}&connectorId={connector_data['connectorId']}&connectorVersion={connector_data['connectorVersion']}&processingDirection={connector_data['processingDirection']}&processingMode={connector_data['processingMode']}"
    call_delete(endpoint)


def fetch_target_factsheets(target_type):
    query = """query {
    allFactSheets (factSheetType: %s) {
        edges {
        node {
            id
            name
            fullName,
            displayName
        }
        }
    }
    }""" % (target_type)
    return {"query": query}

def replace_data_object_keyword(data_object, keyword, replace_keyword):
    return json.loads(json.dumps(data_object).replace(keyword, replace_keyword))


def split(value, delimiter, preserve_index):
    try:
        return value.split(delimiter)[preserve_index]
    except IndexError:
        return value

def format_entry_relations(fs_record):
    display_names = fs_record[relation_type + ':displayName'].split(';')
    display_names = [x for x in display_names if x.strip()]
    entries = []
    for display_name in display_names:
        if display_name in ('', np.NaN):
            import pdb;pdb.set_trace()
        entry =  {
            'id': fs_record['id'],
            'type': relation_type,
            'data': {split(key, ':', 1) : value for key,value in fs_record.items() if key not in ('id', 'type', relation_type + ':displayName', 'displayName')}
        }
        try:
            entry['data']['targetId'] = full_name_id_map[display_name]
        except KeyError:
            try: 
                entry['data']['targetId'] = display_name_id_map[display_name]
            except KeyError:
                entry['data']['targetId'] = ''
                logging.info('match not found for ' + display_name)
                non_match_records.append({'type': relation_type.split('relProjectTo')[1], 'name': display_name})
        entry['data']['targetDisplayName'] = display_name
        entries.append(entry)
    return entries


#### Main Script
filenames = [x for x in os.listdir('run_files') if '.xlsx' in x]

for filename in filenames:

    df = pd.read_excel(f"run_files/{filename}", dtype=str)[1:].fillna("")

    for field in date_fields:
        df[field] = pd.to_datetime(df[field])
        df[field] = df[field].dt.strftime('%Y-%m-%d').fillna("")
        df[field]

    records = df.to_dict(orient="records")

    relation_type = [x for x in records[1].keys() if "rel" in x][0].split(":")[0]

    related_fs_type = relation_type.split("To")[1]

    related_fs_data = get_graphql(fetch_target_factsheets(related_fs_type))

    full_name_id_map =  {x['node']['fullName']: x['node']['id'] for x in related_fs_data['data']['allFactSheets']['edges']}

    display_name_id_map =  {x['node']['displayName']: x['node']['id'] for x in related_fs_data['data']['allFactSheets']['edges']}

    content = [item for sublist in list(map(format_entry_relations, records)) for item in sublist]

    with open('importRelationsConnector.json', 'r') as infile:
        update_relation_connector = json.load(infile)

    fields = [split(x, ':', 1) for x in records[0] if x not in ('id', 'type', relation_type + ':displayName', 'name', 'displayName')]

    update_relation_connector = replace_data_object_keyword(update_relation_connector, 'relationType', relation_type)

    update_template = {'key': {'expr': 'fieldName'}, 'values': [{'expr': '${data.fieldName}'}]}

    update_relation_connector['processors'][0]['updates'] = [replace_data_object_keyword(update_template, 'fieldName', field) for field in fields]

    with open('importRelationLDIF.json', 'r') as infile:
        update_relation_ldif = json.load(infile)

    update_relation_ldif = replace_data_object_keyword(update_relation_ldif, 'relationType', relation_type)

    update_relation_ldif['content'] = content



    with open(update_relation_connector['connectorId'] + '-connector.json', 'w') as outfile:
        json.dump(update_relation_connector, outfile, indent=3)

    with open(update_relation_ldif['connectorId'] + '-Test-ldif.json', 'w') as outfile:
        json.dump(update_relation_ldif, outfile, indent=3)

    put_connector(update_relation_connector)

    result = handle_run(update_relation_ldif, 'inbound')

    delete_connector(update_relation_connector)



nm_df = pd.DataFrame.from_records(non_match_records)
nm_df.to_excel('NonMatchRecords.xlsx', index=False)



