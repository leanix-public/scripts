from requests import get, post
from urllib import parse
from logging import warn, info
from json import dump, load
from auth import get_instance_url

def build_asset_versions_index (token: str, path: str):
    try:
        f =  open(path, 'r')
        idx = load(f)
        return idx
    except FileNotFoundError:
        warn('could not find asset_version file in {path}'.format(path = path))

    url = 'https://store.leanix.net/services/torg/v1/assetversions/versions/REPORT'
    response = post(
        url,
        headers= { 'authorization': 'Bearer {bearer}'.format(bearer=token)}
    )
    response.raise_for_status()
    asset_versions = response.json()
    asset_versions_idx = {}
    for asset_version in asset_versions:
        asset_versions_idx[asset_version['id']] = asset_version
    with open(path, 'w') as f:
        dump(asset_versions_idx, f, indent=4)
    return asset_versions_idx

def fetch_asset_installations (asset_version_id: str, token: str):
    total = -1
    fetched = 0
    has_page = True
    installations = []
    while has_page == True:
        params = { 'searchValue': asset_version_id, 'maxResult': 100, 'startIndex': fetched }
        url = 'https://store.leanix.net/services/torg/v1/assetinstall/find?{query_string}'.format(query_string = parse.urlencode(params))
        response = get(
            url,
            headers= { 'authorization': 'Bearer {bearer}'.format(bearer=token)}
        )
        response.raise_for_status()
        body = response.json()
        total = body['total']
        page_results = body['data']
        fetched = fetched + len(page_results)
        for installation in page_results:
            if (installation['assetVersionId'] == asset_version_id):
                installations.append(installation)
        has_page = fetched < total
    info('asset_version {id} is installed on {workspace_count} workspaces'.format(id=asset_version_id, workspace_count=len(installations)))
    return installations

def get_report_id_for_asset_version_id (asset_version_id: str, asset_versions_idx: dict) -> str:
    report_id = None
    for asset_version in asset_versions_idx.values():
        if asset_version['id'] == asset_version_id:
            report_id = asset_version['assetId']
            break
    if report_id == None:
        raise Exception('could not find asset_version_id {asset_version_id}'.format(asset_version_id=asset_version_id))
    return report_id

def get_latest_asset_version_id (asset_id: str, asset_versions_idx: dict) -> str:
    try:
        asset_version = asset_versions_idx[asset_id]
    except KeyError:
        raise Exception('asset_id {asset_id} could not be found'.format(asset_id=asset_id))
    report_id = asset_version['assetId']
    info('searching the latest version for the report {display_name} v{version} (asset_id {asset_version_id})'.format(display_name=asset_version['displayName'], version=asset_version['version'], asset_version_id=asset_version['id']))
    latest_report_asset_version = None
    for asset_version in asset_versions_idx.values():
        if asset_version['assetId'] == report_id \
            and asset_version['reviewState'] == 'APPROVED' \
            and asset_version['state'] == 'PUBLISHED' \
            and (latest_report_asset_version == None \
            or latest_report_asset_version['version'] < asset_version['version']):
            latest_report_asset_version = asset_version
            if (report_id == None):
                report_id = asset_version
    if (latest_report_asset_version == None):
        raise Exception('could not find the latest version for report id {report_id}'.format(report_id=report_id))
    info('latest version for the report {display_name} is v{version} (asset_id {asset_version_id})'.format(display_name=latest_report_asset_version['displayName'], version=latest_report_asset_version['version'], asset_version_id=latest_report_asset_version['id']))
    return latest_report_asset_version['id']

def install_asset_version_on_workspace (report_id: str, asset_version_id: str, bearer: str):
    instance_url = get_instance_url(bearer)
    url = 'https://store.leanix.net/services/torg/v1/assets/{report_id}/install'.format(report_id=report_id)
    response = post(
        url,
        headers={ 'authorization': 'Bearer {bearer}'.format(bearer = bearer)},
        json={
            'assetType': 'REPORT',
            'assetVersionId': asset_version_id,
            'instanceUrl': instance_url,
            'termsAndConditionsAccepted': True
        }
    )
    response.raise_for_status()
    result = response.json()
    return result


def uninstall_asset_version_from_workspace(installation_id: str, bearer: str):
    url = 'https://store.leanix.net/services/torg/v1/assetinstall/{installation_id}/uninstall'.format(installation_id=installation_id)
    response = post(
        url,
        headers={ 'authorization': 'Bearer {bearer}'.format(bearer = bearer)}
    )
    response.raise_for_status()