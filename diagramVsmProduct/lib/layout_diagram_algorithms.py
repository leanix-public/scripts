import networkx as nx

class LayoutDiagramAlgorithms:
    def __init__(self, svc_product_weight, svc_consumed_api_weight, svc_provided_api_weight) -> None:
        self.SVC_PRODUCT_WEIGHT = svc_product_weight
        self.SVC_CONSUMED_API_WEIGHT = svc_consumed_api_weight
        self.SVC_PROVIDED_API_WEIGHT = svc_provided_api_weight

    def diagram_products(self, products):

        product_graph = nx.Graph()

        product_graph.add_node("productless_services")
        for product_id in products:
            product_graph.add_node(product_id)

        product_positions = nx.circular_layout(product_graph)

        print("PRODUCT GRAPH ===============================")
        print(product_positions)
        print("=============================================")

        return product_positions

    def diagram_full_graph(self, product_positions, products, services, apis):
        full_graph = nx.Graph()

        full_graph.add_node("productless_services")
        for product_id in products:
            full_graph.add_node(product_id)

        for service_id in services:
            full_graph.add_node(service_id)

            for product_id in services[service_id]["product_ids"]:
                full_graph.add_edge(service_id, product_id, weight=self.SVC_PRODUCT_WEIGHT)

            if len(services[service_id]["product_ids"]) == 0:
                full_graph.add_edge(service_id, "productless_services", weight=self.SVC_PRODUCT_WEIGHT)

        for api_id in apis:
            full_graph.add_node(api_id)

            # add the link between the API and the "consuming" service with a small weight to let them be further apart 
            for source_service_id in apis[api_id]["source_ids"]:
                full_graph.add_edge(source_service_id, api_id, weight=self.SVC_CONSUMED_API_WEIGHT)

            # the link between the API and the "providing" service with a larger weight to pull them together
            for target_id in apis[api_id]["target_ids"]:
                full_graph.add_edge(api_id, target_id, weight=self.SVC_PROVIDED_API_WEIGHT)

        iterations = (len(services) + len(apis)) * 100

        # Apply a layout algorithm
        full_graph_positions = nx.spring_layout(full_graph, fixed=product_positions.keys(), pos=product_positions, k=None, iterations=iterations)

        # Print the calculated positions
        print("FULL GRAPH ==================================")
        print(full_graph_positions)
        print("=============================================")

        return full_graph_positions