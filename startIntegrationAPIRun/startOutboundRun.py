import json
import requests
import time
import click
import pandas as pd


def call_post(endpoint, request_url, header, data=False):

    response = requests.post(url=request_url + endpoint,
                             headers=header, data=data)
    response.raise_for_status()
    return response


def call_get(endpoint, request_url, header):
    response = requests.get(url=request_url + endpoint, headers=header)
    response.raise_for_status()
    return response


def create_run(run_config, request_url, header):
    result = call_post("synchronizationRuns", request_url,
                       header, json.dumps(run_config))
    return json.loads(result.text)['id']


def start_run(run_id, request_url, header):
    start_run_endpoint = f'synchronizationRuns/{run_id}/start'
    result = call_post(start_run_endpoint, request_url, header)
    return result.status_code


def check_run_status(run_id, request_url, header, status_response=None):
    print(f'checking status of run {run_id}')
    status_endpoint = f'synchronizationRuns/{run_id}/status'
    status_response = call_get(status_endpoint, request_url, header)
    status_response = json.loads(status_response.text)['status']
    print(status_response)
    if status_response != 'FINISHED':
        time.sleep(5)
        return check_run_status(run_id, request_url, header, status_response)
    elif status_response == 'FAILED':
        print('Run Failed: Validate your connector in LeanIX')
    else:
        return True


def fetch_results(run_id, request_url, header):
    results_endpoint = f'synchronizationRuns/{run_id}/results'
    results_response = call_get(results_endpoint, request_url, header)
    return json.loads(results_response.text)


def export_data(run_config, request_url, header):
    run_id = create_run(run_config, request_url, header)

    if start_run(run_id, request_url, header) == 200:
        if check_run_status(run_id, request_url, header):
            run_results = fetch_results(run_id, request_url, header)
    return run_results


svc_option = click.option(
    '--svc-instance', required=True, prompt=True, hide_input=True)
host_option = click.option('--app-instance', required=True)
api_token_option = click.option('--api-token', required=True)


@click.group()
def cli():
    pass


@cli.command()
@svc_option
@host_option
@api_token_option
def start_run(svc_instance, app_instance, api_token):

    auth_url = f'https://{svc_instance}/services/mtm/v1/oauth2/token'
    request_url = f'https://{app_instance}/services/integration-api/v1/'
    response = requests.post(auth_url, auth=('apitoken', api_token),
                             data={'grant_type': 'client_credentials'})
    response.raise_for_status()
    access_token = response.json()['access_token']
    auth_header = 'Bearer ' + access_token
    header = {'Authorization': auth_header, 'Content-Type': 'application/json'}

    config_df = pd.read_excel('configs.xlsx').fillna('')

    for index, row in config_df.iterrows():

        run_config = {x: row[x] for x in list(config_df)}

        run_results = export_data(run_config, request_url, header)

        out_filename = '_'.join(
            [run_config['connectorId'], run_config['connectorVersion'], 'results.json'])

        with open(out_filename, 'w') as outfile:
            json.dump(run_results, outfile, indent=2)


if __name__ == '__main__':
    cli()
