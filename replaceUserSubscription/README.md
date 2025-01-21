# Replace User Subscription Script

## Overview

The replaceUserSubscriptions allows the user to replace the ownership of subscription. The subscriptions are identified with the users E-Mail address.

You have to provide the E-Mail address of the old user and the one of the new user.

The script then utilizes GraphQL queries to both read and write data to the workspace.

## Prerequisites

Before you start, do the following:

1. Prepare your workspace.
2. Prepare the input data.
3. Set up Python with the following libraries: 
    - `pip install requests`

## Run the Script

To run the script, use the following command:

```bash
LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> NEW_USER=<> OLD_USER=<> python replaceUserSubscription.py
```

## Related Resources

- [GraphQL API](https://docs-eam.leanix.net/reference/graphql-tutorials)
- [Rest APIs](https://docs-eam.leanix.net/reference/rest-apis)
