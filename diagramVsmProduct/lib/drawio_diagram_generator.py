import json
import xml.etree.ElementTree as ET

class DrawIODiagramGenerator:
    def __init__(self, hostname, vsm_workspace, scale_factor) -> None:
        self.HOSTNAME = hostname
        self.VSM_WORKSPACE = vsm_workspace
        self.SCALE_FACTOR = scale_factor
        self.scaled_product_positions = {}
        self.service_count = 0
        self.api_count = 0
        self.UP_TO_DATE_INDICATOR_ID = "up_to_date_indicator"

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

    def graph_information_panels(self, root, full_graph_positions, normalized_data_hash):
        
        min_x = float('inf')
        min_y = float('inf')

        for pos in full_graph_positions.values():
            x, y = pos
            min_x = min(min_x, x)
            min_y = min(min_y, y)

        # Legend
        legend = ET.SubElement(root, "mxCell", {
            "id": "legend",
            "value": "Legend",
            "style": "swimlane;horizontal=0;rounded=0;fillColor=#526179;strokeColor=#526179;fontColor=#ffffff;",
            "parent": "1",
            "vertex": "1"
        })
        
        ET.SubElement(legend, "mxGeometry", {
            "x": str(self.scale_nx_ordinate(min_x) - 140),
            "y": str(self.scale_nx_ordinate(min_y) - 140),
            "width": "140",
            "height": "140",
            "as": "geometry"
        })


        # VSM API
        vsm_api = ET.SubElement(root, "mxCell", {
            "id": "24",
            "value": "VSM API",
            "style": "shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;fixedSize=1;rounded=0;fontColor=#ffffff;strokeColor=#02AFA4;fillColor=#02AFA4;",
            "parent": "legend",
            "vertex": "1"
        })

        ET.SubElement(vsm_api, "mxGeometry", {
            "x": "34",
            "y": "22.9",
            "width": "90",
            "height": "37.1",
            "as": "geometry"
        })

        # VSM Service
        vsm_service = ET.SubElement(root, "mxCell", {
            "id": "25",
            "value": "VSM Service",
            "style": "shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;fixedSize=1;rounded=0;fontColor=#ffffff;strokeColor=#D29270;fillColor=#D29270;",
            "parent": "legend",
            "vertex": "1"
        })

        ET.SubElement(vsm_service, "mxGeometry", {
            "x": "26",
            "y": "80",
            "width": "98",
            "height": "40.1",
            "as": "geometry"
        })

        # Up to date indicator
        up_to_date = ET.SubElement(root, "mxCell", {
            "id": self.UP_TO_DATE_INDICATOR_ID,
            "value": "Up to date",
            "style": "whiteSpace=wrap;html=1;shape=mxgraph.basic.octagon2;align=center;verticalAlign=middle;dx=15;fillColor=#d5e8d4;strokeColor=#82b366;",
            "vertex": "1",
            "parent": "1",
            "content_hash": normalized_data_hash
        })

        ET.SubElement(up_to_date, "mxGeometry", {
            "x": str(self.scale_nx_ordinate(min_x) - 120),
            "y": str(self.scale_nx_ordinate(min_y) - 250),
            "width": "100",
            "height": "100",
            "as": "geometry"
        })

    def graph_product_node(self, root, product, services, full_graph_positions):
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
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')
        for service in services:
            coordinate = full_graph_positions[service["id"]]

            x_ordinate = coordinate[0]
            y_ordinate = coordinate[1]

            min_x = min(min_x, x_ordinate)
            max_x = max(max_x, x_ordinate)
            min_y = min(min_y, y_ordinate)
            max_y = max(max_y, y_ordinate)
        
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

    def graph_services(self, root, parent_id, services, full_graph_positions):
        for service in services:
            # no need to add this again if it has already been added
            if "graphed" in service:
                return
            
            service_id = service["id"]
            service_name = service["name"]

            service_x = self.scale_nx_ordinate(full_graph_positions[service_id][0])
            service_y = self.scale_nx_ordinate(full_graph_positions[service_id][1])

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

    def graph_apis(self, root, apis, full_graph_positions):
        for api_id in apis:
            api = apis[api_id]
            api_name = api["name"]

            api_x = self.scale_nx_ordinate(full_graph_positions[api_id][0])
            api_y = self.scale_nx_ordinate(full_graph_positions[api_id][1])

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

    def generate_drawio_diagram(self, full_graph_positions, products, services, apis, normalized_data_hash):
        print("Generating Diagram in XML format...")

        self.service_count = len(services)
        self.api_count = len(apis)

        drawio_root = self.graph_drawio_root()
        root = ET.SubElement(drawio_root, "root")

        self.graph_default_parent_and_layer(root)

        for product_id in products:

            services_in_product = [services[service_id] for service_id in services if product_id in services[service_id]["product_ids"]]

            product_container_id = self.graph_product_node(root, products[product_id], services_in_product, full_graph_positions)

            # graph the services that belong to this product
            self.graph_services(root, product_container_id, services_in_product, full_graph_positions)

        # graph the services that don't belong to any product
        productless_services = [services[service_id] for service_id in services if len(services[service_id]["product_ids"]) == 0]
        self.graph_services(root, None, productless_services, full_graph_positions)

        # graphs all the APIs and edges between services and APIs
        self.graph_apis(root, apis, full_graph_positions)

        # Put the legend and up to date indicator in the top left
        self.graph_information_panels(root, full_graph_positions, normalized_data_hash)

        graph_string = ET.tostring(drawio_root, encoding="unicode")

        print("DRAW.IO GRAPH ===============================")
        print(graph_string)
        print("=============================================")

        return graph_string
    
    def is_existing_diagram_up_to_date(self, diagram_bookmark, normalized_data_hash):
        parsed_diagram_bookmark = json.loads(diagram_bookmark)

        existing_diagram_id = parsed_diagram_bookmark["data"]["id"]
        existing_diagram = parsed_diagram_bookmark["data"]["state"]["graphXml"]

        # Parse the XML string
        parsed_diagram = ET.fromstring(existing_diagram)

        # Find the mxCell element with the desired id
        mx_cell = parsed_diagram.find(f'.//mxCell[@id="{self.UP_TO_DATE_INDICATOR_ID}"]')

        if mx_cell is not None:
            print("Element found:")
            print(ET.tostring(mx_cell, encoding='unicode'))

            content_hash = mx_cell.get("content_hash")

            if normalized_data_hash != content_hash:
                print(f"DIAGRAM WITH ID '{existing_diagram_id}' IS OUT OF DATE")
            else:
                print("Existing diagram is already up to date")
                return True
        else:
            print(f"No element found with id '{self.UP_TO_DATE_INDICATOR_ID}'")

        return False

    def mark_existing_diagram_outdated(self, diagram_bookmark):
        parsed_diagram_bookmark = json.loads(diagram_bookmark)

        existing_diagram = parsed_diagram_bookmark["data"]["state"]["graphXml"]

        # Parse the XML string
        parsed_diagram = ET.fromstring(existing_diagram)

        # Find the mxCell element with the desired id
        mx_cell = parsed_diagram.find(f'.//mxCell[@id="{self.UP_TO_DATE_INDICATOR_ID}"]')

        if mx_cell is not None:
            print("Element found:")
            print(ET.tostring(mx_cell, encoding='unicode'))

            mx_cell.set("style", "whiteSpace=wrap;html=1;shape=mxgraph.basic.octagon2;align=center;verticalAlign=middle;dx=15;fillColor=#f8cecc;strokeColor=#b85450;")
            mx_cell.set("value", "OUTDATED")

        parsed_diagram_bookmark["data"]["state"]["graphXml"] = ET.tostring(parsed_diagram, encoding='unicode')
        
        return parsed_diagram_bookmark["data"]


    # FYI, a "coordinate" is a pair (hence the "co") of "ordinates"
    def scale_nx_ordinate(self, ordinate):
        return ordinate * (self.service_count + self.api_count) * self.SCALE_FACTOR
