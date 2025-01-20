# Welcome to the SAP LeanIX Scripts Hub

## Overview

Welcome to the LeanIX Scripts Hub. This repository contains Python scripts that allow you to optimize your workflows for [LeanIX](https://www.leanix.net/). Using these scripts, you can automate recurring tasks, reduce manual processes, and enable your team to focus on strategic goals.

To use the scripts in this repository effectively, you should have a basic knowledge of:

- Python
- APIs in general and especially [SAP LeanIX APIs](https://docs-eam.leanix.net/reference/available-apis)
- [GraphQL](https://docs-eam.leanix.net/reference/graphql-tutorials) 
- Running and deploying scripts

## Prerequisites

Most of the scripts need a few prerequisites to be used to their full extent. Every script requires an **API Token** and the **subdomain** (e.g. demo-eu-1) of the workspace your changes are to be made in. In some cases an input file is also required, which too needs to be specified beforehand.

Each of these values are generally defined through environmental variables, but for the specific syntax please refer to the separate README of each script.

### Obtain an API Token

To authenticate your requests to LeanIX APIs, you need an access token. To learn how to obtain an access token, see [Authentication to LeanIX Services](https://docs-eam.leanix.net/reference/authentication-for-managing-api-tokens) in our developer documentation.

To create an API token, you need to have admin access to your LeanIX workspace.

### Prepare Your Environment

Prepare your environment by installing the necessary dependencies. Follow these steps:

1. Install Python.
2. Install needed libraries for the script itself. For this information, please refer to the script specific README.
3. Prepare your workspace and provide necessary input files.

## Using Scripts

The scripts in this repository cover a wide range of typical use cases for the LeanIX application. Use these scripts as a starting point to build custom integrations tailored to your organization's needs.

Depending on the script, you may want to run it on a schedule or in response to certain events. You can do it using various methods, such as cron jobs on Linux, Task Scheduler on Windows, or cloud-based solutions such as Azure Functions or AWS Lambda.

To get started, follow these steps:

1. **Set up configuration:** As mentioned, some scripts may require a configuration file or environment variables to work correctly. Make sure to fill these with your specific values. Instructions are also provided in the specific READMEs.

2. **Run the script:** Once everything is set up, you can run the script using the commands provided in the README of the scripts.

3. **Understand the output:** Each script may output data differently. Some might print data to the console, while others might write data to a file. Make sure to understand how the particular script you're using works.

## Support and Issues

Found an issue or need help? [Open an issue](https://github.com/leanix-public/scripts/issues) in this repository.

If you need further assistance, please [contact LeanIX Support](https://www.leanix.net/support).

## Related Resources

Visit the [LeanIX Developer Documentation](https://docs-eam.leanix.net/reference/welcome-developer-docs) to learn how to get started with custom integrations, explore LeanIX APIs, and view practical examples for typical tasks in our tutorials.

Also join the [Community group for developers](https://community.leanix.net/groups/sap-leanix-developers-84) to never miss out on news and to connect with fellow developers.
