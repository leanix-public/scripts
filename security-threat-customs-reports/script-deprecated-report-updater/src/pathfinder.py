from requests import get, put, delete, post
from urllib import parse
from auth import get_instance_url

# fetches
def build_workspace_reports_index (bearer: str):
    instance_url = get_instance_url(bearer)
    params = { 'sorting': 'updatedAt', 'sortDirection': 'DESC', 'pageSize': 100 }
    url = '{instance}/services/pathfinder/v1/reports?{query_string}'.format(instance=instance_url, query_string = parse.urlencode(params))
    response = get(url, headers= { 'authorization': 'Bearer {bearer}'.format(bearer = bearer)})
    response.raise_for_status()
    body = response.json()
    reports = body['data']
    idx = {}
    for report in reports:
        idx[report['id']] = report
    return idx

def enable_asset_version_on_workspace (asset_version_id: str, report: dict, bearer: str):
    instance_url = get_instance_url(bearer)
    report['enabled'] = True
    url = '{instance}/services/pathfinder/v1/reports/{asset_version_id}'.format(asset_version_id=asset_version_id, instance=instance_url)
    response = put(
        url,
        headers = { 'authorization': 'Bearer {bearer}'.format(bearer = bearer)},
        json = report
    )
    response.raise_for_status()
    body = response.json()
    report = body['data']
    return report

def delete_asset_version_from_workspace (asset_version_id: str, bearer: str):
    instance_url = get_instance_url(bearer)
    url = '{instance}/services/pathfinder/v1/reports/{asset_version_id}'.format(instance=instance_url,asset_version_id=asset_version_id)
    response = delete(url, headers = { 'authorization': 'Bearer {bearer}'.format(bearer = bearer)})
    response.raise_for_status()

def upload_bundle (filepath: str, bearer: str):
    instance_url = get_instance_url(bearer)
    response = post(
        '{instance}/services/pathfinder/v1/reports/upload'.format(instance=instance_url),
        headers = { 'authorization': 'Bearer {bearer}'.format(bearer = bearer) },
        files = { 'file': open(filepath, 'rb') }
    )
    response.raise_for_status()
    data = response.json()
    report_id = data['data']['id']
    return report_id