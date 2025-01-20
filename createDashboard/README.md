# Create Dashboard Script

## Overview

The createDashboard script allows the user to create a dashboard based on the parameters in the given file input.csv.

The script utilizes REST APIs and GraphQL queries to read data, write data and create new dashboards.

## Prerequisites

Before you start, do the following:

1. Put together the input file based on the example given in input.csv.
2. Prepare you workspace according to the [Dashboards](https://docs-eam.leanix.net/docs/dashboards) documentation.
3. Change the facet filters used in `getFilter` according to your needs.
4. Set up Python with the following libraries: 
    - `pip install requests`

## Run the Script

To run the script, use the following command:

```bash
LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> python createDashboard.py
```

## Related Resources

- [GraphQL API](https://docs-eam.leanix.net/reference/graphql-tutorials)
- [Rest APIs](https://docs-eam.leanix.net/reference/rest-apis)
- [SAP LeanIX Dashboards](https://docs-eam.leanix.net/docs/dashboards)
