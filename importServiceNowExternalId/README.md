# Import ServiceNow ExternalID Script

## Overview

The importServiceNowExternalID script allows the user to mass import ServiceNow IDs as external IDs for a specified FactSheet. The changes are given in an input file.

To achieve this, the script utilizes GraphQL queries to fill in the External IDs.

## Prerequisites

Before you start, do the following:

1. Prepare your workspace.
2. Prepare the input file based on the example in ServiceNow.csv
3. Set up Python with the following libraries: 
    - `pip install requests`

## Run the Script

To run the script, use the following command:

```bash
LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> python importServiceNowExternalI.py
```

## Related Resources

- [GraphQL API](https://docs-eam.leanix.net/reference/graphql-tutorials)
- [Rest APIs](https://docs-eam.leanix.net/reference/rest-apis)
