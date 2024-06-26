from typing import Dict
from requests import get, post, put
from urllib import parse
from json import dump, load
from logging import warn, info
from auth import get_claims


def build_workspaces_index (token_idx: Dict[str, str], path: str):
    try:
        f =  open(path, 'r')
        idx = load(f)
        return idx
    except FileNotFoundError:
         warn('could not find workspaces index file in {path}'.format(path = path))

    workspace_index = {}
    for region, token in token_idx.items():
        total = -1
        has_page = True
        region_index = {}
        page = 1
        while has_page == True: 
            params = { 'size': 100, 'page': page, 'sort': 'id-asc' }
            url = 'https://{region}.leanix.net/services/mtm/v1/workspaces?{query_string}'.format(region = region, query_string = parse.urlencode(params))
            response = get(url, headers= { 'authorization': 'Bearer {bearer}'.format(bearer = token)})
            response.raise_for_status()
            body = response.json()
            total = body['total']
            workspaces = body['data']
            for workspace in workspaces:
                region_index[workspace['id']] = region
            info('Region {region} => fetched {fetched} from {total} workspaces'.format(region=region, fetched=len(region_index), total=total))
            has_page = len(region_index) < total
            page = page + 1
        workspace_index = workspace_index | region_index
    with open(path, 'w') as f:
            dump(workspace_index, f, indent=4)
    return workspace_index

def get_impersonation_for_workspace (workspace_id: str, region: str, token: str, reason: str):
    token_claims = get_claims(token)
    user_id = token_claims['principal']['id']
    url = 'https://{region}.leanix.net/services/mtm/v1/impersonations'.format(region = region)
    response = post(
        url,
        headers={ 'authorization': 'Bearer {bearer}'.format(bearer = token)},
        json={
            'workspace': { 'id': workspace_id },
            'impersonator': { 'id': user_id },
            'reason': reason,
            'language': 'en'
        }
    )
    response.raise_for_status()
    body = response.json()
    impersonation_id = body['data']['id']
    access_token = body['data']['accessToken']
    workspace_name = body['data']['workspace']['name']
    return {
        'impersonation_id': impersonation_id,
        'workspace_id': workspace_id,
        'workspace_name': workspace_name,
        'bearer': access_token,
        'region': region
    }

def finalize_impersonation_session (impersonation_id: str, region: str, token_idx: dict):
    token = token_idx[region]
    url = 'https://{region}.leanix.net/services/mtm/v1/impersonations/{impersonation_id}'.format(region = region, impersonation_id=impersonation_id)
    response = put(
        url,
        headers={ 'authorization': 'Bearer {bearer}'.format(bearer = token)}
    )
    response.raise_for_status()