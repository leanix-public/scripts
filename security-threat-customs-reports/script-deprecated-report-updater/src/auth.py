from requests import post
from base64 import b64decode
from json import loads, dump, load
from typing import Dict
from playwright.sync_api import sync_playwright
from logging import warn

def get_claims (bearer_token: str) -> str:
    claims = loads(b64decode(bytes(bearer_token.split('.')[1], 'utf-8') + b'=='))
    return claims

def get_instance_url (bearer_token: str) -> str:
    claims = get_claims(bearer_token)
    instance_url = claims['instanceUrl']
    return instance_url

def get_bearer_using_apitoken (host, apitoken):
    response = post(
        'https://{host}/services/mtm/v1/oauth2/token'.format(host=host),
        auth=('apitoken', apitoken),
        data={'grant_type': 'client_credentials'}
    )
    response.raise_for_status()
    return response.json()['access_token']
    
def build_bearer_token_index(regions: list[str], username: str, password: str, path: str, delete_file: bool = False) -> Dict[str, str]:
    if delete_file == False:
        try:
            f =  open(path, 'r')
            idx = load(f)
            return idx
        except FileNotFoundError:
            warn('could not find token file in {path}'.format(path = path))

    with sync_playwright() as p:
        idx: Dict[str, bearer: str] = {}
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        for i, region in enumerate(regions):
            page.goto('https://{region}-admin.leanix.net/#/workspaces'.format(region=region))
            if i == 0:
                page.wait_for_selector('input[name="identifier"]').fill(username)
                page.locator('input[value="Next"]').click()
                page.wait_for_selector('input[name="credentials.passcode"]').fill(password)
                page.locator('input[value="Verify"]').click()
            
            page.wait_for_url('https://{region}-admin.leanix.net/#/workspaces'.format(region=region), timeout=60000)
            page.wait_for_load_state('networkidle')
            bearer = page.evaluate("() => localStorage.token")
            idx[region] = bearer
        browser.close()
        with open(path, 'w') as f:
            dump(idx, f, indent=4)
        return idx
