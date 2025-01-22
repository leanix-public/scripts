# Modify Attributes on Relations Script

## Overview

The importRelations script allows the user to change attributes, in this case the Technical Suitability, on certain relations. The data is provided in the *import.csv* file. The attribute that is written can be easily change in the script itself.

The exportRelationship script allows the user to export all relations and specific attributes in these relations. To read different attributes, please refer to the query used in `getRelationVariablesToExport`.

The results of the export is stored in *Info.csv*.

To achieve this behavior, the script uses GraphQL queries to both read and write data.

## Prerequisites

Before you start, do the following:

1. Prepare your workspace.
2. Prepare the input file based on the example in *import.csv*.
3. Set up Python with the following libraries: 
    - `pip install requests`

## Run the Script

To run the script, use either of the following commands:

```bash
LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> python exportRelationship.py
LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> IMPORT_FILE=<your input file> python importRelations.py
```

## Related Resources

- [GraphQL API](https://docs-eam.leanix.net/reference/graphql-tutorials)
- [Rest APIs](https://docs-eam.leanix.net/reference/rest-apis)
