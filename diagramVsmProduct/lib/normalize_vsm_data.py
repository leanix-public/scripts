
import hashlib
import json


class Normalization:
    def __init__(self, product_name, product_link_name):
        self.PRODUCT_NAME = product_name
        self.PRODUCT_LINK_NAME = product_link_name
        self.normalized_products = {}
        self.normalized_services = {}
        self.normalized_apis = {}
        self.normalized_data_hash = None
        self.main_product_id = None
        self.main_product_link_id = None
        self.diagram_id = None

    def hash_string(self, input_string):
        sha256 = hashlib.sha256()
        sha256.update(input_string.encode('utf-8'))
        return sha256.hexdigest()

    def normalize_vsm_data(self, graphql_response):
        print("Normalizing VSM Data...")

        data = json.loads(graphql_response)
        products = data["data"]["products"]

        for product in products:
            self.normalize_product(product)

        self.normalized_data_hash = self.hash_string(str(self.normalized_products)+str(self.normalized_services)+str(self.normalized_apis))

        return self.normalized_products, self.normalized_services, self.normalized_apis, self.normalized_data_hash, self.main_product_id, self.main_product_link_id, self.diagram_id

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

                    link_url = link["url"]
                    url_parts = link_url.split('/')
                    self.diagram_id = url_parts[-1]

        if "relProductToService" in product:
            for service in product["relProductToService"]:
                # normalize service
                service = service["service"]

                self.normalize_service(service, product["id"])

        self.normalized_products[product["id"]] = norm_product

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

        else: 
            # This service has never been processed, so create it and add it to the collection
            norm_service = {
                "id": service["id"],
                "product_ids": product_ids,
                "name": service["name"]
            }

            self.normalized_services[service["id"]] = norm_service


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

