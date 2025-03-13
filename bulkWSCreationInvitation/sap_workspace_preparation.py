import requests
import json
import time
import pandas as pd
import logging
from datetime import datetime,timedelta


# Configure the logger
logging.basicConfig(
    filename='app.log',               # Specify the log file name
    level=logging.INFO,               # Set the logging level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s'  # Define the log message format
)


class LeanIX:
    def __init__(self, base_url, auth_url, api_token):
        self.base_url = base_url
        self.auth_url = auth_url
        self.api_token = api_token
        self.access_token = self._get_token()
        self.max_retries = 10
        self.retry_count = 0
        self.rate_limit_wait = 0.05  # 50ms wait to stay under 20 requests/second
        self.templateid = "671e0091-690e-44db-8d62-0efbb1a31857"

    def _handle_request(self, request_func, *args, **kwargs):
        """Generic handler for API requests with retry logic"""
        try:
            response = request_func(*args, **kwargs)

            if response.status_code == 401 and self.retry_count < self.max_retries:
                print(
                    f"Authentication failed, retrying... (Attempt {self.retry_count + 1}/{self.max_retries})"
                )
                self.retry_count += 1
                self.access_token = self._get_token()

                # Update authorization header with new token
                if "headers" in kwargs:
                    kwargs["headers"]["Authorization"] = f"Bearer {self.access_token}"

                # Recursive call with updated token
                return self._handle_request(request_func, *args, **kwargs)

            # Reset retry count on successful request
            self.retry_count = 0
            return response

        except Exception as e:
            if self.retry_count < self.max_retries:
                print(
                    f"Request failed, retrying... (Attempt {self.retry_count + 1}/{self.max_retries})"
                )
                self.retry_count += 1
                time.sleep(1)  # Wait 1 second before retry
                return self._handle_request(request_func, *args, **kwargs)
            raise e

    def _make_request(self, method, url, **kwargs):
        """Make an API request with rate limiting"""
        time.sleep(self.rate_limit_wait)  # Rate limiting delay
        return self._handle_request(
            lambda url, **kw: requests.request(method, url, **kw), url, **kwargs
        )

    def _get_token(self):
        """Get access token using API token"""
        response = requests.post(
            self.auth_url,
            auth=("apitoken", self.api_token),
            data={"grant_type": "client_credentials"},
        )

        if response.status_code == 200:
            return response.json()["access_token"]
        raise Exception(f"Authentication failed: {response.text}")

    def _run_graphql(self, base_url, json_data):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        request_url = base_url+'/services/pathfinder/v1/graphql'
        try:
            response = requests.post(url=request_url, headers=headers, data=json_data)
            response.raise_for_status()
        except Exception as ex:
            print(ex)
            raise
        return response

    def get_user(self, user_id, subdomain):
        # Get workspace data from MTM based on its id
        template_url = f"{subdomain}/users/{user_id}"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        response = self._make_request("GET", template_url, headers=headers)
        response_json = response.json()

        print("Status code (fetching user): " + str(response.status_code))
        if response.status_code not in [200, 201]:
            raise Exception(f"Workspace fetching failed with status {response.status_code}: {response.text}")
        del response_json["data"]["permissions"]
        return response_json

    def get_workspace(self, workspace_id, subdomain):
        # Get workspace data from MTM based on its id
        template_url = f"{subdomain}/workspaces/{workspace_id}"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        response = self._make_request("GET", template_url, headers=headers)
        response_json = response.json()

        print("Status code (fetching workspace): " + str(response.status_code))
        if response.status_code not in [200, 201]:
            raise Exception(f"Workspace fetching failed with status {response.status_code}: {response.text}")
        return response_json

    def addSupportPermission(self, workspace_id, subdomain, user_id):
        url = f"{subdomain}/permissions"
        permission_data = {
            "user": self.get_user(user_id, subdomain)["data"],
            "workspace": self.get_workspace(workspace_id, subdomain)["data"],
            "role": "ADMIN",
            "status": "ACTIVE",
        }
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        response = self._make_request("POST", url, headers=headers, json=permission_data)
        if response:
            response_json = response.json()
            return response_json
        return response

    def createApiToken(self, workspace_id, subdomain, support_id):
        api_url = f"{subdomain}/apiTokens"
        apitoken_data = {
            "description": "Scripting",
            "userId": support_id,
            "workspaceId": workspace_id,
            "expiry": str((datetime.now() + timedelta(days=1)).isoformat()),
            "type": "[ApiTokens] Create API Token",
        }
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        response = self._make_request("POST", api_url, headers=headers, json=apitoken_data)
        response_json = response.json()
        #print(response_json)
        return response_json["data"]["token"]
    
    def check_inventory(self, subdomain):
        graphql_query =  """
                    query MyQuery {
                      allFactSheets(first: 1, filter: {displayName: "Asset Management"}) {
                        edges {
                          node {
                            displayName
                          }
                        }
                      }
                    }
                    """

        data = {"query" : graphql_query}  
        base_url = f"https://{subdomain}"    
        response = self._run_graphql(base_url, json.dumps(data))
        #print(response)
        response = response.json()
        if 'errors' in response:
           logging.info(response['errors'][0]['message'])
        
        expected_return = {
                              "data": {
                                "allFactSheets": {
                                  "edges": [
                                    {
                                      "node": {
                                        "displayName": "Asset Management"
                                      }
                                    }
                                  ]
                                }
                              }
                            }

        
        return response == expected_return

    def getInviteUserData(self, user_id, user, ws, authRole, updateMessage):
        data = """{
             "host": {
                 "id": "%s"
             },
             "user": {
                 "email": "%s"
             },
             "workspace": {
                 "id": "%s"
             },
             "permission": {
                 "role": "%s"
             },
             "message": "%s"
            }"""%(user_id, user, ws, authRole, updateMessage)
        return data

    def inviteUser(self, updateUserInfo, SUBDOMAIN):
        invite_url = f"https://{SUBDOMAIN}/services/mtm/v1/idm/invite?silent=false"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        try:
          response = requests.post(url=invite_url, headers=headers, data=updateUserInfo)
          response.raise_for_status()
        except requests.exceptions.HTTPError as err:
          # print(request_url)
          # print(json.dumps(data))
          print(err)
          exit
        #print(response.json())
        return response.json() 


def main():
    # Map to create correct MTM url
    mtm_url_map = {
        "southeastasia": "https://sg.leanix.net/services/mtm/v1",
        "westeurope": "https://eu-17.leanix.net/services/mtm/v1",
        "germanywestcentral": "https://demo-de.leanix.net/services/mtm/v1",
        "eastus": "https://us-11.leanix.net/services/mtm/v1",
        "brazilsouth": "https://br.leanix.net/services/mtm/v1",
    }

    # Map to map each region to the correct api token
    api_token_map = {
        "southeastasia": "",
        "westeurope": "",
        "germanywestcentral": "",
        "eastus": "",
        "brazilsouth": "",
    }

    # Map to map the region to the subdomain
    subdomain_map = {
        "southeastasia": "sap-apm-sg.leanix.net",
        "westeurope": "sap-apm-eu.leanix.net",
        "germanywestcentral": "sap-apm-de.leanix.net",
        "eastus": "sap-apm-us.leanix.net",
        "brazilsouth": "sap-apm-br.leanix.net",
    }

    support_id_map = {
        "southeastasia": "55e8b344-3ba1-4e47-b920-c45dba8fc35a",
        "westeurope": "1e3f0aef-b870-4320-be28-c0412f8db088",
        "germanywestcentral": "9e4ec4dd-6ad5-4670-a2a5-56c16a5beba3",
        "eastus": "1e3f0aef-b870-4320-be28-c0412f8db088",
        "brazilsouth": "4cac3f2d-462a-466b-934b-4c0c7d1667a9",
    }
    
    file_path = input("Please provide the file Path for the excle file: ")
    df = pd.read_excel(file_path)
    results = []
    count = 0
    for index, row in df.iloc[0:].iterrows():

        # Check 10 at a time
        if count >= 10:
            #break
            print("\nWaiting...")
            time.sleep(1)
            count = 0

        # Get input from user
        workspace_id = row["workspace_id"]
        email = row["email"]

        # Get the instance id based on the given region and set correct mtm url
        region = row["region"]
        base_url = mtm_url_map[region]
        auth_url = base_url + "/oauth2/token"

        # Create instance of LeanIX
        creator = LeanIX(base_url, auth_url, api_token_map[region])


        # Track success status
        status = {
            "apitoken": {"success": False},
            "inventory": {"success": False},
            "invitation": {"success": False},
        }



        try:
            print("\n=== Starting workspace checking process ===\n")

            # Create new api token in workspace and fetch a new bearer token for specified workspace
            print("\n1. Creating apitoken for workspace...")
            permission = creator.addSupportPermission(workspace_id, mtm_url_map[region], support_id_map[region])
            #continue
            creator = LeanIX(base_url, auth_url, creator.createApiToken(workspace_id, mtm_url_map[region], support_id_map[region]))
            status["apitoken"].update(
                {"success": True}
            )

            # Check if workspace was provisioned without errors
            print("\n2. Checking workspace...")
            inventory_success = creator.check_inventory(subdomain_map[region])
            status["inventory"].update(
                {"success": inventory_success}
            )

            # Invite user to workspace
            print("\n3. Inviting user workspace...")
            invitation_message = """Dear LeanIX user,\\n\\n we are happy to invite you to the APM SAP LeanIX workspace. This is a dedicated workspace only for account planning (as required according to the new SAP account planning template) for the account specified in the workspace name (account name and BP ID) owned by the EA-RISE or AA assigned to the account. As a workspace owner, please make sure to invite other account team members with the access rights required and guide them on how to use LeanIX.\\n\\n You will receive a separate email with details on documentation and a recording of an enablement session to support the migration of APM work from another LeanIX workspace to this one to ensure compliance.\\n\\n Your SAP LeanIX team"""
            creator.inviteUser(creator.getInviteUserData(support_id_map[region], email, workspace_id, "ADMIN", invitation_message), subdomain_map[region])
            status["invitation"].update(
                {"success": True}
            )

            print(index)
            # Print final status report
            print("\n=== Process Summary ===")
            print("\nWorkspace Creation Status:")
            print("------------------------")
            print(
                f"Workspace:    {'✓' if status['apitoken']['success'] else '✗'}"
            )
            print(
                f"Workspace:    {'✓' if status['inventory']['success'] else '✗'}"
            )
            print(
                f"Workspace:    {'✓' if status['invitation']['success'] else '✗'}"
            )


            if all(item["success"] for item in status.values()):
                print(f"\n✅ All checks completed successfully! User {email} was invited.")
                logging.info(f'Checked and sent out invite for workspace ID: {workspace_id} (User: {email})')
            else:
                failed_steps = [
                    step for step, data in status.items() if not data["success"]
                ]
                print(
                    f"\n⚠️  Process completed with warnings. Failed steps: {', '.join(failed_steps)}"
                )

        except Exception as e:
            # Print error status with completed steps
            print("\n❌ Error occurred during process!")
            logging.info(f'Failed for workspace ID: {workspace_id} (User: {email})')
            print(f"Error details: {str(e)}")
            print("\nCompleted steps before error:")
            for step, data in status.items():
                status_symbol = "✓" if data["success"] else "✗"
                if step == "account" and data["success"]:
                    print(f"- {step}: {status_symbol} {data['name']}")
                elif step == "workspace" and data["success"]:
                    print(f"- {step}: {status_symbol} {data['name']}")
                else:
                    print(f"- {step}: {status_symbol}")
        
        count += 1
        time.sleep(3)

    result_df = pd.DataFrame(results)
    output_file = file_path.replace(".xlsx", "_output.xlsx")
    df_existing = pd.read_excel(output_file)
    df_combined = pd.concat([df_existing, result_df], ignore_index=True)
    df_combined.to_excel(output_file, index=False)
    #logging.info(f"Results written to {output_file}")


if __name__ == "__main__":
    main()
