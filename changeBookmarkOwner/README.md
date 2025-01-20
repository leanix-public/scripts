# Change Bookmark Owners Script

## Overview

The changeBookmarkOwners script allows the user to mass change the owners of a list of bookmarks. The input file provides the id of the bookmark itself and the id of the user that is to be set as the new owner.

The script uses REST APIs to change the owners based on the given input file.

## Prerequisites

Before you start, do the following:

1. Create a list of the IDs of the Bookmarks and its new owners under the name bookmarkUpdates.csv. An example can be found in the given bookmarkUpdates.csv.
2. Set up Python with the following libraries: 
    - `pip install requests`

## Run the Script

To run the script, use the following command:

```bash
LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> python changeBookmarkOwners.py
```

## Related Resources

- [GraphQL API](https://docs-eam.leanix.net/reference/graphql-tutorials)
- [Rest APIs](https://docs-eam.leanix.net/reference/rest-apis)
