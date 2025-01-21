# Update ITC Relations Script

## Overview

The updateITCRelations script allows the user to import multiple ITComponent to Technology Stack (Tech Categories) relations.

The relations to be imported are specified in the Book1.csv file. 

To achieve this, the script uses GraphQl queries to both read and write data in the workspace.

## Prerequisites

Before you start, do the following:

1. Prepare your workspace.
2. Prepare your input and provide the correct IDs. An example can be found in the Book1.csv file.
3. Set up Python with the following libraries: 
    - `pip install requests`

## Run the Script

To run the script, use the following command:

```bash
$ LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> IMPORT_FILE=<your input file> python import.py
```

## Related Resources

- [GraphQL API](https://docs-eam.leanix.net/reference/graphql-tutorials)
- [Rest APIs](https://docs-eam.leanix.net/reference/rest-apis)
