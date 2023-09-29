import json
from . import mtm_api
import requests

class LeanIxEamApi:
    def __init__(self, hostname, workspace_name, api_token):
        self.hostname = hostname
        self.workspace_name = workspace_name
        self.api_token = api_token
        self.mtm_api = mtm_api.LeanIxMtmApi(hostname, api_token)
        self.bookmarks_base_url = f"https://{self.hostname}/services/pathfinder/v1/bookmarks"

    def fetch_existing_diagram(self, diagram_id) -> str:
        url = f"{self.bookmarks_base_url}/{diagram_id}"
        headers = {
            "Authorization": f"Bearer {self.mtm_api.access_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return response.text
    
    def upload_new_diagram(self, drawio_diagram, diagram_name) -> str:
        url = self.bookmarks_base_url
        headers = {
            "Authorization": f"Bearer {self.mtm_api.access_token}",
            "Content-Type": "application/json"
        }
        body = {
            "name": diagram_name,
            "type": "VISUALIZER",
            "groupKey": "freedraw",
            "state": {
                "version": 2,
                "graphXml": drawio_diagram
            },
            "autoUpdate": True,
            "isJustMigratedFromLegacy": False,
            "workingCopy": None,
            "description": "",
            "i18nKey": None,
            "predefined": False,
            "readonly": False,
            "defaultSharingPriority": None,
            "permittedReadUserIds": [],
            "permittedWriteUserIds": [],
            "views": 0,
            "replaySequence": 0,
            "temporary": False,
            "oDataEnabled": False
        }
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()

        diagram_id = json.loads(response.text)["data"]["id"]

        diagram_url = f"https://{self.hostname}/{self.workspace_name}/diagrams/freedraw/{diagram_id}"

        return diagram_url
    
    def update_existing_diagram(self, diagram_id, diagram_bookmark):
        url = f"{self.bookmarks_base_url}/{diagram_id}"
        headers = {
            "Authorization": f"Bearer {self.mtm_api.access_token}",
            "Content-Type": "application/json"
        }
        response = requests.put(url, headers=headers, json=diagram_bookmark)
        response.raise_for_status()

        return response.text
        