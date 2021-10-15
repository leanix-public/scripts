import requests
import json
import time
import pandas as pd
import os




with open('configs.json', 'r') as infile:
    configs = json.load(infile)
    api_token = configs['api_token']
    date_fields = configs['date_fields']
    domain = configs['domain']
    region = configs['region']

auth_url = f'https://{region}-svc.leanix.net/services/mtm/v1/oauth2/token'
request_base = f'https://{domain}/'



response = requests.post(
    auth_url, auth=("apitoken", api_token), data={"grant_type": "client_credentials"}
)

response.raise_for_status()
access_token = response.json()["access_token"]
auth_header = "Bearer " + access_token


header = {"Authorization": auth_header, "Content-Type": "application/json"}


def call_post(request_url, data=False):
    
    response = requests.post(
        url=request_url, headers=header, data=json.dumps(data)
    )
    try:
        response.raise_for_status()
        return json.loads(response.text)
    except json.decoder.JSONDecodeError:
        pass


def call_put(request_url, data=False):
    
    response = requests.put(
        url=request_url, headers=header, data=json.dumps(data)
    )
    try:
        response.raise_for_status()
        return json.loads(response.text)
    except json.decoder.JSONDecodeError:
        pass

def call_delete(request_url):
    response = requests.delete(
        url=request_url, headers=header)
    try:
        response.raise_for_status()
        return json.loads(response.text)
    except json.decoder.JSONDecodeError:
        pass



def call_get(request_url, endpoint):
    response = requests.get(url=request_url + endpoint, headers=header)
    response.raise_for_status()
    return response

def get_graphql(query):
    endpoint = request_base + 'services/pathfinder/v1/graphql'
    response = call_post(endpoint, query)
    return response

 
def create_run(run_config):
    create_run_endpoint = request_base + "services/integration-api/v1/synchronizationRuns"
    result = call_post(create_run_endpoint, run_config)
    return json.loads(result.text)["id"]


def start_run(run_id):
    start_run_endpoint = request_base + "services/integration-api/v1/synchronizationRuns/%s/start" % (run_id)
    result = call_post(start_run_endpoint)
    return result.status_code


def check_run_status(run_id, status_response=None):
    print("checking status")
    status_endpoint = request_base + "services/integration-api/v1/synchronizationRuns/%s/status" % (run_id)
    status_response = call_get(status_endpoint)
    status_response = json.loads(status_response.text)["status"]
    print(status_response)
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
    entries = []
    for display_name in display_names:
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
                print('match not found for ' + display_name)
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

    with open(update_relation_ldif['connectorId'] + '-ldif.json', 'w') as outfile:
        json.dump(update_relation_ldif, outfile, indent=3)

    put_connector(update_relation_connector)

    result = handle_run(update_relation_ldif, 'inbound')

    delete_connector(update_relation_connector)




