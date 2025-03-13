import requests
import json
import time
import pandas as pd
import logging


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

    def create_workspace(self, contract_id, customer_name, instance_id):
        """Create a new workspace using the RISE template"""
        workspace_name = customer_name
        template_url = f"https://snapshot-manager.leanix.net/templates/{self.templateid}/instance"

        workspace_data = {
            "contractId": contract_id,
            "targetWorkspaceName": workspace_name,
            "reason": "SAP RISE Delivery",
            "workspaceType": "LIVE",
            "instanceId": instance_id,
        }

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        response = self._make_request("POST", template_url, headers=headers, json=workspace_data)
        response_json = response.json()

        print("Status code: " + str(response.status_code))
        if response.status_code not in [200, 201]:
            raise Exception(f"Workspace creation failed with status {response.status_code}: {response.text}")

        if 'errors' in response_json and response_json['errors'] and len(response_json['errors']) > 0:
            raise Exception(f"Workspace creation had errors: {response_json['errors']}")

        return workspace_name  # Return the generated workspace name

    def get_workspace_id(self, workspace_name, attempt=1, max_attempts=4):
        """
        Get workspace ID by name using GET /workspaces endpoint with pagination
        Uses recursion to retry up to max_attempts times with 5 second delays
        
        Args:
            workspace_name (str): Name of workspace to find
            attempt (int): Current attempt number (default: 1)
            max_attempts (int): Maximum number of attempts (default: 4)
        """
        def get_workspaces_page(page):
            """Helper function to get a page of workspaces"""
            url = f"{self.base_url}/workspaces?page={page}&size=100&sort=name-asc&q={workspace_name}"
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            }

            response = self._make_request("GET", url, headers=headers)
            if response.status_code != 200:
                raise Exception(f"Failed to get workspaces: {response.text}")
            
            response_json = response.json()
            
            # Check for errors in response
            if response_json.get("errors") and len(response_json["errors"]) > 0:
                raise Exception(f"Workspace extraction had errors: {response_json['errors']}")
            
            return response_json

        # Wait 5 seconds before each attempt (except first attempt)
        if attempt > 1:
            print(f"Workspace not found, retry {attempt}/{max_attempts} after 5 seconds...")
            time.sleep(5)
        else:
            print("Waiting for workspace to be available...")
            time.sleep(5)

        # Start with page 1 and continue until no more data
        page = 1
        while True:
            response_data = get_workspaces_page(page)
            
            # If no more workspaces, break the loop
            if not response_data.get("data"):
                break
            
            # Check current page for workspace
            for workspace in response_data.get("data", []):
                if workspace.get("name") == workspace_name:
                    return workspace.get("id")
            
            # Move to next page
            page += 1

        # If workspace not found and we haven't reached max attempts, try again
        if attempt < max_attempts:
            return self.get_workspace_id(workspace_name, attempt + 1, max_attempts)
        
        # If we've exhausted all attempts, raise exception
        raise Exception(f"Workspace '{workspace_name}' not found after {max_attempts} attempts")

    def get_workspace(self, workspace_id, subdomain):
        # Get workspace data from MTM based on its id
        template_url = f"https://{subdomain}.leanix.net/services/mtm/v1/workspaces/{workspace_id}"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        response = self._make_request("GET", template_url, headers=headers)
        response_json = response.json()

        print("Status code (fetching workspace): " + str(response.status_code))
        if response.status_code not in [200, 201]:
            raise Exception(f"Workspace fetching failed with status {response.status_code}: {response.text}")

        return json.dumps(response_json)

    def update_workspace(self, workspace_id, workspace_data, subdomain):
        # Get workspace data from MTM based on its id
        template_url = f"https://{subdomain}.leanix.net/services/mtm/v1/workspaces/{workspace_id}"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        response = self._make_request("PUT", template_url, headers=headers, json=json.loads(workspace_data))

        print("Status code (update workspace): " + str(response.status_code))
        if response.status_code not in [200, 201]:
            raise Exception(f"Workspace updating failed with status {response.status_code}: {response.text}")

        return response.status_code

    def update_workspace_data(self, workspace_data, domain_id):
        updated_workspace_data = json.loads(workspace_data)["data"]

        updated_workspace_data["invitationOnly"] = True
        updated_workspace_data["domain"] = {"id": domain_id}

        return json.dumps(updated_workspace_data)


def main():
    # Map region to full region name
    region_map = {
        "MEE": "germanywestcentral",
        "EU": "westeurope",
        "US": "eastus",
        "LAC": "brazilsouth",
        "APAC": "southeastasia",
        "CS APAC": "southeastasia",
        "CS Latin America": "brazilsouth",
        "CS North America": "eastus",
    }

    # Map from region to instance id
    instance_map = {
        "southeastasia": "35812637-5d75-4e2d-952f-98ab622079b9",
        "westeurope": "0ca889e2-2e12-4df9-af9f-785e251ffc42",
        "germanywestcentral": "ff1ee8b0-9ac3-4d6a-9ad9-69713fb0008e",
        "eastus": "1da90595-651c-4c3d-920d-8172d8146f76",
        "brazilsouth": "2d33123e-b9ec-45e5-a90c-1e1fdde55b0d",
    }

    # Map from region to domain id
    domain_map = {
        "southeastasia": "02fd3ba3-38d8-47d9-b9f1-7349adbd543b",
        "westeurope": "9091ca65-1472-4fdf-8be7-d859bc428a71",
        "germanywestcentral": "3f3287e5-a948-4c41-b4e3-1cc403a42106",
        "eastus": "af11af36-48bf-49f1-9b3b-43592ce2f579",
        "brazilsouth": "b7f9808e-57bb-4ac8-b4ef-c4d32a5d3eda",
    }

    # Map to create correct MTM url
    mtm_url_map = {
        "southeastasia": "https://sg.leanix.net/services/mtm/v1",
        "westeurope": "https://demo-eu-6.leanix.net/services/mtm/v1",
        "germanywestcentral": "https://demo-de.leanix.net/services/mtm/v1",
        "eastus": "https://demo-us-1.leanix.net/services/mtm/v1",
        "brazilsouth": "https://br.leanix.net/services/mtm/v1",
    }

    subdomain_map = {
        "southeastasia": "sg",
        "westeurope": "demo-eu-6",
        "germanywestcentral": "demo-de",
        "eastus": "demo-us-1",
        "brazilsouth": "br",
    }

    # Map to map each region to the correct api token
    api_token_map = {
        "southeastasia": "",
        "westeurope": "",
        "germanywestcentral": "",
        "eastus": "",
        "brazilsouth": "",
    }
    
    contract_map = {
        "southeastasia": "9bf0112e-d28f-4336-a6c1-db8b6b732c6e",
        "westeurope": "0b58d20a-6cb8-4e74-8d2d-3e1327251248",
        "germanywestcentral": "9b8597db-f848-4de6-96bb-3ee8fffca95b",
        "eastus": "a3312934-c98b-448b-a0bd-3fa67a3b182e",
        "brazilsouth": "03f7c4b9-415e-4d16-b066-e2f77cddcddc",
    }

    file_path = input("Please provide the file Path for the excle file: ")
    df = pd.read_excel(file_path)
    results = []
    count = 0
    for index, row in df.iloc[0:].iterrows():

        # Provision 10 at a time
        if count >= 10:
            #break
            print("\nWaiting...")
            time.sleep(120)
            count = 0

        # Get input from user
        customer_name = row["Workspace Name"]

        # Get the instance id based on the given region and set correct mtm url
        region = region_map[row["Region"]]
        instance_id = instance_map[region]
        base_url = mtm_url_map[region]
        auth_url = base_url + "/oauth2/token"

        # Create instance of LeanIX
        creator = LeanIX(base_url, auth_url, api_token_map[region])

        # Track success status
        status = {
            "workspace": {"success": False, "id": None, "name": None},
        }

        try:
            print("\n=== Starting workspace creation process ===\n")

            # Create workspace
            print(f"\n1. Creating workspace {customer_name}...")
            workspace_name = creator.create_workspace(contract_map[region], customer_name, instance_id)

            # Get workspace ID
            print("\n2. Getting workspace ID...")
            workspace_id = creator.get_workspace_id(workspace_name)
            status["workspace"].update(
                {"success": True, "id": workspace_id, "name": workspace_name}
            )
            print(
                f"{index} ✓ Workspace created successfully: {workspace_name} (ID: {workspace_id})"
            )

            # Print final status report
            print("\n=== Process Summary ===")
            print("\nWorkspace Creation Status:")
            print("------------------------")
            print(
                f"Workspace:    {'✓' if status['workspace']['success'] else '✗'} {status['workspace']['name']}"
            )

            if all(item["success"] for item in status.values()):
                print("\n✅ All operations completed successfully!")
                print(
                    f"\nWorkspace URL: https://demo-eu-6.leanix.net/{workspace_name} NOT ACCURATE!" #WIP
                )
                results.append(
                    {
                        "workspace_name": workspace_name,
                        "workspace_id": workspace_id,
                        "region": region,
                    })
                logging.info(f'Created workspace {workspace_name} (ID: {workspace_id})')
            else:
                failed_steps = [
                    step for step, data in status.items() if not data["success"]
                ]
                print(
                    f"\n⚠️  Process completed with warnings. Failed steps: {', '.join(failed_steps)}"
                )
                logging.info(f'Failed creating workspace {customer_name}')

            print("Turning off invitation only and setting domain of workspace")
            ws = creator.get_workspace(workspace_id, subdomain_map[region])
            code = creator.update_workspace(workspace_id, creator.update_workspace_data(ws, domain_map[region]), subdomain_map[region])
            if str(code) != "200":
                print("\n❌ Error occurred during workspace updating process!")
                logging.info(f'Failed updating workspace {customer_name}')


        except Exception as e:
            # Print error status with completed steps
            print("\n❌ Error occurred during process!")
            logging.info(f'Failed creating workspace {customer_name}')
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

    result_df = pd.DataFrame(results)
    output_file = file_path.replace(".xlsx", "_output.xlsx")
    df_existing = pd.read_excel(output_file)
    df_combined = pd.concat([df_existing, result_df], ignore_index=True)
    df_combined.to_excel(output_file, index=False)
    #logging.info(f"Results written to {output_file}")


if __name__ == "__main__":
    main()
