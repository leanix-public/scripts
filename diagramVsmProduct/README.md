## Diagram VSM Product

The `Diagram VSM Product` is a script to visualize the VSM workspace. Given a product from your VSM workspace, it uploads a diagram of the product’s connected services and APIs into EAM workspace (with a link back to the product in VSM). Please feel free to download this script and make adjustments to best fit your use case.

## Usage

1. Download the [diagramVsmProduct subdirectory](https://github.com/leanix-public/scripts/tree/668aa9ed05c6479ae23bf9f8d350aa0c85065b0d/diagramVsmProduct)
2. Create a config.json file following the example below:
```
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
```
3. Build and run the container

### Environment Variables

`product_name`: This is the exact name of the product in VSM.

`hostname`: The host name of your LeanIX VSM workspaces. (e.g. For `https://acme.leanix.net` you would provide `acme.leanix.net`)

`vsm_workspace`: The name of the VSM workspace. It can be seen in the URL of the workspace (e.g., for `https://acme.leanix.net/acmevsmworkspace/valuestreams` you would provide `acmevsmworkspace`)

`eam_workspace`: The name of the EAM workspace. It can be seen in the URL of the workspace (e.g., for `https://acme.leanix.net/acmeeamworkspace/dashboard` you would provide `acmeeammworkspace`)

`vsm_api_token`: API token with **MEMBER** or **ADMIN** rights from your VSM workspace. (see settings > technical users).

`eam_api_token`: API token with **MEMBER** or **ADMIN** rights from your EAM workspace. (see settings > technical users)

`product_link_name`: The name of the link from the product in VSM to the diagram in EAM

`skip_if_latest_diagram_up_to_date` : When true (recommended), skips generating a new diagram is the latest is up to date

`svc_product_weight`: Weight of the link between the product and the service. The product and the service are closer when the weight is larger, and further when the weight is smaller. 

`svc_provided_api_weight`: Weight of the link between the API and the "providing" service. The API and "providing service' are closer with a larger weight and further with a smaller weight.

`svc_consumed_api_weight`: Weight of the link between the API and the "consuming" service. The API and "consuming service are closer together with a larger weight and further with a smaller weight.

`scale_factor`: Scale factor for the diagram

`dry_run`: When set to true, runs the script without creating a diagram
