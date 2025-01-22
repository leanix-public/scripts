# Tag 2 Attribute Script

## Overview

The tag2Attributes script allows the user to map a list of fields to certain attributes. These attributes are then read and tags are assigned based on these readings.

The loadMapping script reads currently actively set tags and attributes to then create a mapping based on this data.

## Prerequisites

Before you start, do the following:

1. Prepare your workspace.
2. Load Mapping: 
  - creates a CSV mapping of all Tags and single/multiple select fields 
  - map the tags you want to change to the right fields and delete all other information from the file
3. Update Tags:
  - make sure to have the right FS-type in the GraphQl call
  - make sure to reference the right csv file
4. Prepare the input data and provide the FactSheet ID, the path of the field that is to be mutated and the value itself.
5. Set up Python with the following libraries: 
    - `pip install requests`

## Run the Script

To run the script, use the following command:

```bash
LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> FACTSHEET_ID=<> PATH=<> EXTERNAL_ID=<> python setExternalIds.py
```

## Related Resources

- [GraphQL API](https://docs-eam.leanix.net/reference/graphql-tutorials)
- [Rest APIs](https://docs-eam.leanix.net/reference/rest-apis)
