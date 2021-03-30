import json
import requests
import time
import click


def access_configs():
    with open('access.json', 'r') as infile:
        access_data = json.load(infile)
    return access_data

def auth_url():
    domain = access_configs()['domain']
    return f"https://{domain}/services/mtm/v1/oauth2/token"

def request_url():
    domain = access_configs()['domain']
    return f"https://{domain}/services/integration-api/v1/"

def api_token():
    return access_configs()['apitoken']

def authenticate():
    response = requests.post(auth_url(), auth=('apitoken', api_token()),
                             data={'grant_type': 'client_credentials'})

    response.raise_for_status()
    access_token = response.json()['access_token']

    return {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}

def call_post(endpoint, header, data=False):
    response = requests.post(
        url=request_url() + endpoint, headers=header, data=data)
    response.raise_for_status()
    return response

def call_get(endpoint, header):
    response = requests.get(url=request_url() + endpoint, headers=header)
    response.raise_for_status()
    return response

def create_run(run_config, header):
    result = call_post(endpoint="synchronizationRuns",
                       data=json.dumps(run_config), header=header)
    return json.loads(result.text)['id']

def start_run(run_id, header):
    start_run_endpoint = 'synchronizationRuns/%s/start' % (run_id)
    result = call_post(endpoint=start_run_endpoint, header=header)
    return result.status_code

def check_run_status(run_id, header, status_response=False):
    print('checking status')
    status_endpoint = 'synchronizationRuns/%s/status' % (run_id)
    status_response = call_get(status_endpoint, header)
    status_response = json.loads(status_response.text)['status']
    print(status_response)
    if status_response != 'FINISHED':
        time.sleep(5)
        return check_run_status(run_id, status_response=status_response, header=header)
    else:
        return True

def fetch_results(run_id, header):
    results_endpoint = 'synchronizationRuns/%s/results' % (run_id)
    results_response = call_get(results_endpoint, header)
    return json.loads(results_response.text)

def handle_run(ldif_data, processing_direction, header):

    run_id = create_run(ldif_data, header)
    if start_run(run_id, header) == 200:
        if check_run_status(run_id, header) and processing_direction == 'outbound':
            return fetch_results(run_id, header)

ldif_option = click.option('--ldif-filename', required=True)

@click.group()
def cli():
    pass

@cli.command()
@ldif_option
def run_integration_api(ldif_filename):

    header = authenticate()

    with open(ldif_filename, 'r') as infile:
        ldif_data = json.load(infile)

    connector_id = ldif_data['connectorId']
    connector_version = ldif_data['connectorVersion']
    processing_direction = ldif_data['processingDirection']

    if processing_direction == 'outbound':
        run_results = handle_run(
            ldif_data=ldif_data, processing_direction='outbound', header=header)
        with open('_'.join([connector_id + connector_version]) + '.json', 'w') as outfile:
            json.dump(run_results, outfile, ensure_ascii=False, indent=4)
    else:
        handle_run(ldif_data, processing_direction='inbound', header=header)

if __name__ == '__main__':
    cli()
