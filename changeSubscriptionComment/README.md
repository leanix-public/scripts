# Change Subscription Comment Script

## Overview

The changeSubscriptionComment script allows the user to change the comment of every active subscription to the comment set on the subscription type.

To achieve this, the script utilizes GraphQL queries to both read and write information in the workspace.

## Prerequisites

Before you start, do the following:

1. Completely set up the subscriptions and the subscription types themselves.
2. Set up Python with the following libraries: 
    - `pip install requests`

## Run the Script

To run the script, use the following command:

```bash
LEANIX_API_TOKEN=<YOUR API TOKEN> LEANIX_SUBDOMAIN=<YOUR INSTANCE> python changeSubscriptionComment.py
```

## Related Resources

- [GraphQL API](https://docs-eam.leanix.net/reference/graphql-tutorials)
- [Rest APIs](https://docs-eam.leanix.net/reference/rest-apis)
