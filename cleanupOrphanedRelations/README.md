# Cleanup Orphaned Relations Script

## Overview

The cleanupOrphanedRelations script allows the user to cleanup orphaned relations throughout the entire workspace.

To achieve this, the script utilizes GraphQL queries to both read and write information in the workspace.

## Prerequisites

Before you start, do the following:

1. Set up Python with the following libraries: 
    - `pip install requests`

## Run the Script

To run the script, use the following command:

```bash
LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> python cleanupOrphanedRelations.py
```

## Related Resources

- [GraphQL API](https://docs-eam.leanix.net/reference/graphql-tutorials)
- [Rest APIs](https://docs-eam.leanix.net/reference/rest-apis)
