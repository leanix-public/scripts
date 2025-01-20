# Import Metrics Script

## Overview

The importMetrics script allows you to mass import Metrics based on a given input file.

The script uses REST APIs to create new metrics.

## Prerequisites

Before you start, do the following:

1. Prepare your workspace.
3. Prepare the input file based on the example in Book1.csv.
2. Set up Python with the following libraries: 
    - `pip install requests`

## Run the Script

To run the script, use the following command:

```bash
LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> IMPORT_FILE=<your input file> python importMetrics.py
```

## Related Resources

- [GraphQL API](https://docs-eam.leanix.net/reference/graphql-tutorials)
- [Rest APIs](https://docs-eam.leanix.net/reference/rest-apis)
- [SAP LeanIX Metrics](https://docs-eam.leanix.net/docs/metrics)
