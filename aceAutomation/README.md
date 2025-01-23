# Populate ACEs Script

## Overview

The populateaces script enables you to automate the assignment of ACEs to FactSheets. Based on set relations to UserGroup FactSheets, an ACE is set on Application, ITComponent, and Project FactSheets.

For now, the script assigns both read and write ACEs on the same basis. However, this behaviour can easily be changed in the script itself.

This script utilizes REST APIs and GraphQL to create new ACEs, read data from the workspace and mutate the given FactSheets.

## Prerequisites

Before you start, do the following:

1. Enable Virtual Workspaces in your Workspace.
2. Create ACEs based on the names of the User Groups that are to be used for ACEs.
3. Set all relevant relations that should indicate the need for an ACE.
4. Set up Python with the following libraries: 
    - `pip install requests`

## Run the Script

To run the script, use the following command:

```bash
LEANIX_API_TOKEN=<YOUR API TOKEN> LEANIX_SUBDOMAIN=<YOUR INSTANCE> python populateaces.py
```

## Related Resources

- [Virtual Workspaces](https://docs-eam.leanix.net/docs/virtual-workspaces)
- [GraphQL API](https://docs-eam.leanix.net/reference/graphql-tutorials)
- [Rest APIs](https://docs-eam.leanix.net/reference/rest-apis)
