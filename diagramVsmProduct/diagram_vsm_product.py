import json
from datetime import datetime
from lib import vsm_api, eam_api, normalize_vsm_data, layout_diagram_algorithms, drawio_diagram_generator

'''
Config File Example:
config.json

{
  "product_name": "<EXACT NAME OF THE PRODUCT IN VSM>",
  "hostname": "<HOST NAME OF YOUR VSM WORKSPACES>",
  "vsm_workspace": "<THE NAME OF YOUR VSM WORKSPACE>",
  "eam_workspace": "<THE NAME OF YOUR EAM WORKSPACE>",
  "vsm_api_token": "<TECHNICAL USER TOKEN TO VSM>",
  "eam_api_token": "<TECHNICAL USER TOKEN TO EAM>",
  "product_link_name": "Product Architecture Diagram in EAM",
  "skip_if_latest_diagram_up_to_date" : true,
  "svc_product_weight": 4,
  "svc_provided_api_weight": 2,
  "svc_consumed_api_weight": 1,
  "scale_factor": 40,
  "dry_run": false
}
'''

def generate_and_upload_diagram(config):
    vsm_interface = vsm_api.LeanIxVsmApi(config["hostname"], config["vsm_api_token"])
    eam_interface = eam_api.LeanIxEamApi(config["hostname"], config["eam_workspace"], config["eam_api_token"])
    normalizer = normalize_vsm_data.Normalization(config["product_name"], config["product_link_name"])
    layout_algoriths = layout_diagram_algorithms.LayoutDiagramAlgorithms(config["svc_product_weight"], config["svc_consumed_api_weight"], config["svc_provided_api_weight"])
    drawio_generator = drawio_diagram_generator.DrawIODiagramGenerator(config["hostname"], config["vsm_workspace"], config["scale_factor"])
    
    graphql_response = vsm_interface.fetch_vsm_data(config["product_name"])

    normalized_products, normalized_services, normalized_apis, normalized_data_hash, main_product_id, main_product_link_id, diagram_id = normalizer.normalize_vsm_data(graphql_response)

    if diagram_id is not None:
        diagram_bookmark = eam_interface.fetch_existing_diagram(diagram_id)

        up_to_date = drawio_generator.is_existing_diagram_up_to_date(diagram_bookmark, normalized_data_hash)
        
        if not up_to_date:
            updated_diagram_bookmark = drawio_generator.mark_existing_diagram_outdated(diagram_bookmark)
            
            eam_interface.update_existing_diagram(diagram_id, updated_diagram_bookmark)

        elif config["skip_if_latest_diagram_up_to_date"]:
            print("No need to continue since the latest diagram is up to date")
            return
    
    product_positions = layout_algoriths.diagram_products(normalized_products)
    full_graph_positions = layout_algoriths.diagram_full_graph(product_positions, normalized_products, normalized_services, normalized_apis)

    drawio_diagram = drawio_generator.generate_drawio_diagram(full_graph_positions, normalized_products, normalized_services, normalized_apis, normalized_data_hash)
    time_stamp = f"{datetime.now().strftime('%m-%d %H:%M')}"
    diagram_name = f"{config['product_name']} - {time_stamp} - VSM Product Diagram"

    if config["dry_run"] is False:
        diagram_url = eam_interface.upload_new_diagram(drawio_diagram, diagram_name)

        vsm_interface.update_vsm_product(config["product_link_name"], diagram_url, main_product_id, main_product_link_id)

# Load the configuration from a JSON file
with open("config.json") as config_file:
    config = json.load(config_file)

# Run the main function with the loaded configuration
generate_and_upload_diagram(config)