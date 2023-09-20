import json
import sys
import xml.etree.ElementTree as ET
import requests
import jwt
from datetime import datetime
import networkx as nx
from playwright.sync_api import sync_playwright

'''
Config File Example:
config.json

{
  "product_name": "<EXACT NAME OF THE PRODUCT IN VSM>",
  "hostname": "<HOST NAME OF YOUR VSM WORKSPACES>",
  "vsm_workspace": "<THE NAME OF YOUR VSM WORKSPACE>",
  "eam_workspace": "<THE NAME OF YOUR EAM WORKSPACE>",
  "vsm_api_token": "<TECHNICAL USER TOKEN TO VSM",
  "eam_api_token": "<TECHNICAL USER TOKEN TO EAM",
  "product_link_name": "Product Architecture Diagram in EAM",
  "svc_product_weight": 4,
  "svc_provided_api_weight": 2,
  "svc_consumed_api_weigth": 1,
  "scale_factor": 40,
  "dry_run": false
}
'''

# Create a class to encapsulate the functionality
class LeanIXDiagramGenerator:
    def __init__(self, config):
        self.AUTH_TOKEN = config['bearer_token'] if 'bearer_token' in config else None
        self.PRODUCT_NAME = config["product_name"]
        self.HOSTNAME = config["hostname"]
        self.VSM_WORKSPACE = config["vsm_workspace"]
        self.EAM_WORKSPACE = config["eam_workspace"]
        self.VSM_API_TOKEN = config["vsm_api_token"]
        self.EAM_API_TOKEN = config["eam_api_token"]
        self.SVC_PRODUCT_WEIGHT = config["svc_product_weight"]
        self.SVC_PROVIDED_API_WEIGHT = config["svc_provided_api_weight"]
        self.SVC_CONSUMED_API_WEIGHT = config["svc_consumed_api_weigth"]
        self.PRODUCT_LINK_NAME = config["product_link_name"]
        self.SCALE_FACTOR = config["scale_factor"]
        self.DRY_RUN = config["dry_run"]
        self.main_product_id = None
        self.main_product_link_id = None
        self.launch_url = None
        self.normalized_products = {}
        self.normalized_services = {}
        self.normalized_apis = {}
        self.product_graph = nx.Graph()
        self.full_graph = nx.Graph()
        self.product_positions = None
        self.scaled_product_positions = {}
        self.full_graph_positions = None

    # Authenticate and run the GraphQL query
    def authenticate(self, token):
        
        url = f"https://{self.HOSTNAME}/services/mtm/v1/oauth2/token"
        auth = ("apitoken", token)
        data = {"grant_type": "client_credentials"}

        response = requests.post(url, auth=auth, data=data)
        response.raise_for_status()

        return response.json()["access_token"]
        

    def sign_in(self, token):
        access_token = self.authenticate(token) if self.AUTH_TOKEN is None else self.AUTH_TOKEN

        self.launch_url = self.get_launch_url(self.HOSTNAME, access_token)
        return bool(self.launch_url)

    def get_launch_url(self, leanix_instance, bearer_token):
        if not leanix_instance or not isinstance(leanix_instance, str):
            error_msg = 'no leanix instance was provided!'
            print("\033[91m{}\033[00m".format(error_msg), file=sys.stderr)
            raise ValueError(error_msg)
        if not bearer_token or not isinstance(bearer_token, str):
            error_msg = 'no valid Bearer Token was provided!'
            print("\033[91m{}\033[00m".format(error_msg), file=sys.stderr)
            raise ValueError(error_msg)

        decoded_token = jwt.decode(bearer_token, options={"verify_signature": False})
        workspace_name = ''
        if (decoded_token and 'principal' in decoded_token and
                'permission' in decoded_token['principal'] and
                'workspaceName' in decoded_token['principal']['permission']):
            workspace_name = decoded_token['principal']['permission']['workspaceName']
        else:
            error_msg = 'could not retrieve workspace name from bearer token!'
            print("\033[91m{}\033[00m".format(error_msg), file=sys.stderr)
            raise ValueError(error_msg)

        host = 'https://' + leanix_instance
        bearer_token_hash = f'#access_token={bearer_token}' if bearer_token else ''
        base_launch_url = f'{host}/{workspace_name}/dashboard'
        launch_url = base_launch_url + bearer_token_hash
        return launch_url

    def send_vsm_graphql_request(self, access_token, query, variables=None):

        url = f"https://{self.HOSTNAME}/services/vsm-compass/v1/graphql"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        request_json = {"query": query, **({"variables": variables} if variables is not None else {})}
        response = requests.post(url, headers=headers, json=request_json)
        response.raise_for_status()

        return response.text

    def fetch_vsm_data(self, access_token):
        print("Fetching VSM Data...")

        query = '''
query ProductModel($productname: String) {
  products(where: {name: {_eq: $productname}}) {
    id
    name
    links {
      name
      id
    }
    readOnlyLinksV2(where: {source: {_like: "%eam%"}}) {
      url
    }
    relProductToService {
      service {
        id
        name
        relServiceToApi {
          api {
            id
            name
            relApiToService {
              role
              service {
                id
                name
                relServiceToProduct {
                  product {
                    id
                    name
                    readOnlyLinksV2(where: {source: {_like: "%eam%"}}) {
                      url
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
    '''

        response = self.send_vsm_graphql_request(access_token, query, variables={"productname": self.PRODUCT_NAME})

        return response
    
    def update_vsm_product(self, access_token, diagram_url, product_id=None, existing_link_id=None):
        print('Updating VSM Product...')

        insert_query = '''
mutation UpsertProductLink($values: LinksInsertInput!) {
  insertLinksOne(object: $values) {
    id
    url
    name
    __typename
  }
}
'''

        update_query = '''
mutation UpsertProductLink($id: uuid, $values: LinksSetInput) {
  updateLinks(where: {id: {_eq: $id}}, _set: $values) {
    returning {
      id
      url
      name
      __typename
    }
    __typename
  }
}
'''

        variables = {
            "values": {
                "name": self.PRODUCT_LINK_NAME,
                "url": diagram_url
            }
        }

        if existing_link_id is not None:
            variables["id"] = existing_link_id

            self.send_vsm_graphql_request(access_token, update_query, variables)
        elif product_id is not None:
            variables["values"]["vsmObjectId"] = product_id

            self.send_vsm_graphql_request(access_token, insert_query, variables)


    def normalize_vsm_data(self, graphql_response):
        print("Normalizing VSM Data...")

        data = json.loads(graphql_response)
        products = data["data"]["products"]

        for product in products:
            self.normalize_product(product)

    def normalize_product(self, product):
        # Check if this product already exists
        if product["id"] in self.normalized_products:
            return
        
        # Extract the eam_id
        app_id = None
        if len(product["readOnlyLinksV2"]) > 0:
            link_url = product["readOnlyLinksV2"][0]["url"]
            url_parts = link_url.split('/')
            app_id = url_parts[-1]

        # Build the normalized product object
        norm_product = {
            "main_product": self.PRODUCT_NAME == product["name"],
            "vsm_id": product["id"],
            "eam_id": app_id,
            "name": product["name"]
        }

        if norm_product["main_product"] == True:
            self.main_product_id = product["id"]

            # Find if there is an existing link to the diagram on the product and save the link id for later
        if "links" in product:
            for link in product["links"]:
                if link["name"] == self.PRODUCT_LINK_NAME:
                    self.main_product_link_id = link["id"]

        if "relProductToService" in product:
            for service in product["relProductToService"]:
                # normalize service
                service = service["service"]

                self.normalize_service(service, product["id"])

        self.normalized_products[product["id"]] = norm_product

        # add the product to both graphs
        self.product_graph.add_node(product["id"])
        self.full_graph.add_node(product["id"])

    def normalize_service(self, service, parent_product_id=None):
        service_id = service["id"]

        product_ids = []
        if "relServiceToProduct" in service and len(service["relServiceToProduct"]):
            for sub_product_rel in service["relServiceToProduct"]:
                sub_product = sub_product_rel["product"]
                sub_product_id = sub_product["id"]
                
                product_ids.append(sub_product_id)

                self.normalize_product(sub_product)
        elif parent_product_id is not None:
            product_ids = [parent_product_id]

        # Determine if this service was partially processed already 
        if service_id in self.normalized_services:
            # This service has been partially processed already, 
            # so finish processing it and add additional product ids where necessary
            norm_service = self.normalized_services[service_id]

            existing_product_ids = norm_service["product_ids"]

            for product_id in product_ids:
                if product_id not in existing_product_ids:
                    existing_product_ids.append(product_id)
                    self.full_graph.add_edge(service_id, product_id, weight=5)

        else: 
            # This service has never been processed, so create it and add it to the collection
            norm_service = {
                "id": service["id"],
                "product_ids": product_ids,
                "name": service["name"]
            }

            self.normalized_services[service["id"]] = norm_service

            # add the service to the full graph
            self.full_graph.add_node(service["id"])

            # link the service with the products it supports with a high weight to keep them the closest together
            for product_id in product_ids:
                self.full_graph.add_edge(service_id, product_id, weight=self.SVC_PRODUCT_WEIGHT)


        if "relServiceToApi" in service:
            for api in service["relServiceToApi"]:
                self.normalize_api(api["api"])

    def normalize_api(self, api):
        if api["id"] in self.normalized_apis:
            return # already added, save CPU time and skip past

        source_ids = []
        target_ids = []
        for service_rel in api["relApiToService"]:
            # Extract service data
            service = service_rel["service"]
            service_id = service["id"]
            
            # Be sure service has been processed
            self.normalize_service(service)

            # Add this service id to the API's source or target based on the role
            if service_rel["role"] == "consumer":
                source_ids.append(service_id)
            elif service_rel["role"] == "provider":
                target_ids.append(service_id)

        # Build API object
        norm_api = {
            "id": api["id"],
            "name": api["name"],
            "source_ids": source_ids,
            "target_ids": target_ids
        }

        # Add API to collection
        self.normalized_apis[api["id"]] = norm_api

        # add the API to the graph
        self.full_graph.add_node(api["id"])

        # add the link between the API and the "consuming" service with a small weight to let them be further apart
        for source_id in source_ids:
            self.full_graph.add_edge(source_id, api["id"], weight=self.SVC_CONSUMED_API_WEIGHT)

        # the link between the API and the "providing" service with a larger weight to pull them together
        for target_id in target_ids:
            self.full_graph.add_edge(api["id"], target_id, weight=self.SVC_PROVIDED_API_WEIGHT)

    # Functions to create the draw.io diagram
    def graph_drawio_root(self):
        drawio_root = ET.Element("mxGraphModel")
        drawio_root.set("dx", "1412")        
        drawio_root.set("dy", "925")
        drawio_root.set("grid", "1")
        drawio_root.set("gridSize", "10")
        drawio_root.set("guides", "1")
        drawio_root.set("tooltips", "1")
        drawio_root.set("connect", "1")
        drawio_root.set("arrows", "1")
        drawio_root.set("fold", "1")
        drawio_root.set("page", "0")
        drawio_root.set("pageScale", "1")
        drawio_root.set("pageWidth", "850")
        drawio_root.set("pageHeight", "1100")
        drawio_root.set("math", "0")
        drawio_root.set("shadow", "0")
        return drawio_root

    def graph_default_parent_and_layer(self, root):
        default_parent = ET.SubElement(root, "mxCell")
        default_parent.set("id", "0")

        default_layer = ET.SubElement(root, "mxCell")
        default_layer.set("id", "1")
        default_layer.set("parent", "0")

    def graph_product_node(self, root, product, services):
        product_vsm_id = product["vsm_id"]
        product_name = product["name"]
        product_eam_id = product["eam_id"]
        product_linked_to_factsheet = False
        container_id = product_vsm_id

        product_parent_node = root

        if product_eam_id is not None:

            product_parent_node = ET.SubElement(root, "object", {
                "type": "factSheet",
                "label": product_name,
                "factSheetType": "Application",
                "factSheetId": product_eam_id,
                "id": product_eam_id
            })

            product_linked_to_factsheet = True
            container_id = product_eam_id

        # Instead of using the original locations, redraw it based on the min and max of all the services
        min_x = None
        min_y = None
        max_x = None
        max_y = None
        for service in services:
            coordinate = self.full_graph_positions[service["id"]]

            x_ordinate = coordinate[0]
            y_ordinate = coordinate[1]

            min_x = x_ordinate if min_x is None or x_ordinate < min_x else min_x
            min_y = y_ordinate if min_y is None or y_ordinate < min_y else min_y
            max_x = x_ordinate if max_x is None or x_ordinate > max_x else max_x
            max_y = y_ordinate if max_y is None or y_ordinate > max_y else max_y
        
        product_x = self.scale_nx_ordinate(min_x) - 50
        product_y = self.scale_nx_ordinate(min_y) - 50

        self.scaled_product_positions[container_id] = [product_x, product_y]

        product_node = ET.SubElement(product_parent_node, "mxCell", {
            "id": product_vsm_id,
            "style": "leanix_color_Application;swimlane;",
            "vertex": "1",
            "parent": "1"
        })

        if not product_linked_to_factsheet:
            product_node.set("value", product_name)

        product_geometry = ET.SubElement(product_node, "mxGeometry", {
            "x": str(product_x),
            "y": str(product_y),
            "width": str(self.scale_nx_ordinate(max_x - min_x) + 200),
            "height": str(self.scale_nx_ordinate(max_y - min_y) + 150),
            "as": "geometry"
        })

        return container_id

    def graph_services(self, root, parent_id, services):
        for service in services:
            # no need to add this again if it has already been added
            if "graphed" in service:
                return
            
            service_id = service["id"]
            service_name = service["name"]

            service_x = self.scale_nx_ordinate(self.full_graph_positions[service_id][0])
            service_y = self.scale_nx_ordinate(self.full_graph_positions[service_id][1])

            if parent_id is not None:
                product_position = self.scaled_product_positions[parent_id]
                product_x = product_position[0]
                product_y = product_position[1]

                service_x = abs(product_x - service_x)
                service_y = abs(product_y - service_y)


            service_user_object = ET.SubElement(root, "UserObject", {
                "label": service_name,
                "link": f"https://{self.HOSTNAME}/{self.VSM_WORKSPACE}/valuestreams/Services/{service_id}",
                "id": service_id
            })

            service_node = ET.SubElement(service_user_object, "mxCell", {
                "style": "shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;fixedSize=1;rounded=0;fillColor=#D29270;strokeColor=#D29270;fontColor=#FFFFFF;fontStyle=1",
                "vertex": "1",
                "parent": parent_id if parent_id is not None else "1"
            })

            service_geometry = ET.SubElement(service_node, "mxGeometry", {
                "x": str(service_x),
                "y": str(service_y),
                "width": "130",
                "height": "50",
                "as": "geometry"
            })

            service["graphed"] = True

    def graph_apis(self, root, apis):
        for api_id in apis:
            api = apis[api_id]
            api_name = api["name"]

            api_x = self.scale_nx_ordinate(self.full_graph_positions[api_id][0])
            api_y = self.scale_nx_ordinate(self.full_graph_positions[api_id][1])

            api_user_object = ET.SubElement(root, "UserObject", {
                "label": api_name,
                "link": f"https://{self.HOSTNAME}/{self.VSM_WORKSPACE}/valuestreams/Apis?selectedItem={api_id}",
                "id": f"{api_id}"
            })

            api_node = ET.SubElement(api_user_object, "mxCell", {
                "style": "shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;fixedSize=1;rounded=0;fillColor=#02AFA4;strokeColor=#02AFA4;fontColor=#FFFFFF;fontStyle=1",
                "vertex": "1",
                "parent": "1"
            })

            api_geometry = ET.SubElement(api_node, "mxGeometry", {
                "x": str(api_x),
                "y": str(api_y),
                "width": "130",
                "height": "50",
                "as": "geometry"
            })

            for source_service_id in api["source_ids"]:

                edge = ET.SubElement(root, "mxCell", {
                    "style": "rounded=0;orthogonalLoop=1;jettySize=auto;html=1;elbow=vertical;", 
                    "edge": "1", 
                    "source": source_service_id, 
                    "target": api_id, 
                    "parent": "1" })
                
                edge_geometry = ET.SubElement(edge, "mxGeometry", {
                    "relative": "1",
                    "as": "geometry"
                })

            for target_service_id in api["target_ids"]: 

                edge = ET.SubElement(root, "mxCell", {
                    "style": "rounded=0;orthogonalLoop=1;jettySize=auto;html=1;elbow=vertical;", 
                    "edge": "1", 
                    "source": api_id, 
                    "target": target_service_id, 
                    "parent": "1" })
                
                edge_geometry = ET.SubElement(edge, "mxGeometry", {
                    "relative": "1",
                    "as": "geometry"
                })

    def generate_drawio_diagram(self):
        print("Generating Diagram in XML format...")

        drawio_root = self.graph_drawio_root()
        root = ET.SubElement(drawio_root, "root")

        self.graph_default_parent_and_layer(root)

        for product_id in self.normalized_products:

            services_in_product = [self.normalized_services[service_id] for service_id in self.normalized_services if product_id in self.normalized_services[service_id]["product_ids"]]

            product_container_id = self.graph_product_node(root, self.normalized_products[product_id], services_in_product)

            # graph the services that belong to this product
            self.graph_services(root, product_container_id, services_in_product)

        # graph the services that don't belong to any product
        productless_services = [self.normalized_services[service_id] for service_id in self.normalized_services if len(self.normalized_services[service_id]["product_ids"]) == 0]
        self.graph_services(root, None, productless_services)

        self.graph_apis(root, self.normalized_apis)

        graph_string = ET.tostring(drawio_root, encoding="unicode")

        print("DRAW.IO GRAPH ===============================")
        print(graph_string)
        print("=============================================")

        return graph_string

    def diagram_products(self):
        self.product_graph.add_node("productless_services")

        self.product_positions = nx.circular_layout(self.product_graph)

        print("PRODUCT GRAPH ===============================")
        print(self.product_positions)
        print("=============================================")

    def diagram_full_graph(self):

        self.full_graph.add_node("productless_services")

        for service_id in self.normalized_services:
            if len(self.normalized_services[service_id]["product_ids"]) == 0:
                self.full_graph.add_edge(service_id, "productless_services", weight=self.SVC_PRODUCT_WEIGHT)

        iterations = (len(self.normalized_services) + len(self.normalized_apis)) * 100

        # Apply a layout algorithm
        self.full_graph_positions = nx.spring_layout(self.full_graph, fixed=self.product_positions.keys(), pos=self.product_positions, k=None, iterations=iterations)

        # Print the calculated positions
        print("FULL GRAPH ==================================")
        print(self.full_graph_positions)
        print("=============================================")

    # Upload the diagram to LeanIX
    def upload_diagram(self, drawio_xml):
        print("Uploading Diagram...")

        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            page = context.new_page()

            try:
                self.sign_in(self.EAM_API_TOKEN)
            except Exception as e:
                print(e)
                exit()

            page.goto(self.launch_url)
            page.wait_for_url("**dashboard**")
            workspace_url = page.url.split("/dashboard")[0]


            time_stamp = f"{datetime.now().strftime('%m-%d %H:%M')}"
            diagram_name = f"{self.PRODUCT_NAME} - {time_stamp} - VSM Product Diagram"

            # Open file selector & import diagram
            page.goto(f"{workspace_url}/diagrams/freedraw/new?returnUrl=%2Fdiagrams%2Foverview%2Fnew&version=2")
            page.frame_locator("lx-editor iframe").get_by_text("Extras", exact=True).click()
            page.frame_locator("lx-editor iframe").get_by_role("cell", name="Edit Diagram...").click()
            # page.frame_locator("lx-editor iframe").get_by_role("cell", name="Device...").click()

            iframe_content = page.query_selector("body > lx-app > div.appContainer.container-fluid.noAppPadding > lx-diagrams-container > div > div.diagramWrapper.ng-star-inserted > lx-diagrams-host > lx-lazy-load-web-component > lx-diagrams-entry > lx-editor > iframe").content_frame()
            iframe_content.fill("body > div.geDialog > div > textarea", drawio_xml)
            page.frame_locator("lx-editor iframe").get_by_role("button", name="OK").click()

            # Set diagram settings and save the file
            page.frame_locator("lx-editor iframe").get_by_role("button", name="Save").click()
            page.get_by_placeholder("Enter a name").fill(diagram_name)
            page.locator("lx-single-select").get_by_role("textbox").click()
            page.get_by_text("Unrestricted").click()
            page.get_by_label("Automatically update (labels & view colors)").uncheck()
            page.get_by_label("Automatically update (labels & view colors)").check()
            page.get_by_role("button", name="Save").click()
            page.wait_for_url("**/freedraw/**")

            # page.wait_for_load_state()

            # page.wait_for_url_not_containing("new")

            # page.get_by_text(diagram_name)

            desired_pattern = r'https://[^/]+/[^/]+/diagrams/freedraw/[0-9a-fA-F-]+$'

            page.wait_for_function(f'''
    () => {{
        const desiredPattern = new RegExp('{desired_pattern}');
        return desiredPattern.test(window.location.href);
    }}
    ''')

            diagram_url = page.url

            browser.close()

            return diagram_url

    # FYI, a "coordinate" is a pair (hence the "co") of "ordinates"
    def scale_nx_ordinate(self, ordinate):
        return ordinate * (len(self.normalized_services) + len(self.normalized_apis)) * self.SCALE_FACTOR

    # Main function to generate and upload the diagram
    def generate_and_upload_diagram(self):

        access_token = self.authenticate(self.VSM_API_TOKEN)
        graphql_response = self.fetch_vsm_data(access_token)

        self.normalize_vsm_data(graphql_response)

        self.diagram_products()
        self.diagram_full_graph()

        drawio_diagram = self.generate_drawio_diagram()

        if self.DRY_RUN is False:
            diagram_url = self.upload_diagram(drawio_diagram)

            self.update_vsm_product(access_token, diagram_url, self.main_product_id, self.main_product_link_id)

# Load the configuration from a JSON file
with open("config.json") as config_file:
    config = json.load(config_file)

# Create an instance of the LeanIXDiagramGenerator class and run the main function
generator = LeanIXDiagramGenerator(config)
generator.generate_and_upload_diagram()
