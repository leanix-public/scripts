from . import mtm_api
import requests

class LeanIxVsmApi:
    def __init__(self, hostname, api_token):
        self.hostname = hostname
        self.api_token = api_token
        self.mtm_api = mtm_api.LeanIxMtmApi(hostname, api_token)

    def send_vsm_graphql_request(self, query, variables=None):

        url = f"https://{self.hostname}/services/vsm-compass/v1/graphql"
        headers = {
            "Authorization": f"Bearer {self.mtm_api.access_token}",
            "Content-Type": "application/json"
        }
        request_json = {"query": query, **({"variables": variables} if variables is not None else {})}
        response = requests.post(url, headers=headers, json=request_json)
        response.raise_for_status()

        return response.text

    def fetch_vsm_data(self, product_name):
        print("Fetching VSM Data...")

        query = '''
query ProductModel($productname: String) {
  products(where: {name: {_eq: $productname}}) {
    id
    name
    links {
      name
      id
      url
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

        response = self.send_vsm_graphql_request(query, variables={"productname": product_name})

        return response
    
    def update_vsm_product(self, product_link_name, diagram_url, product_id=None, existing_link_id=None):
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
                "name": product_link_name,
                "url": diagram_url
            }
        }

        if existing_link_id is not None:
            variables["id"] = existing_link_id

            self.send_vsm_graphql_request(update_query, variables)
        elif product_id is not None:
            variables["values"]["vsmObjectId"] = product_id

            self.send_vsm_graphql_request(insert_query, variables)
