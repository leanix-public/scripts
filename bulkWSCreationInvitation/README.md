# Bulk Workspace preparations

DISCLAIMER: Both scripts were created in the scope of SAP Account Planning and thus are mostly fitted to the involved domains, instances, accounts, and regions.

The creation script allows you to create workspaces based on an input Excel File.

The invitation script allows you to create necessary permissions, check the workspace with a simple GraphQL query, and invite specific users. 

## Creation script
The creation script reguires an input file based on which the workspaces are created. An example can be found in Boo1.xlsx.

The script follows this workflow:
1. It creates a workspace with the snapshot manager under a given contract, workspace name, instance and template id.
2. It waits for MTM to create said workspace and retrieves the workspace id
3. It changes the domain of the workspace

At the end, you receive an output file with the worspace name, the region, and the workspace id.
In case that fails, there is also logging to a app.log file (needs to be created beforehand!).


## Preparation script
The preparation script checks the workspace, creates necessary permissions in MTM and lastly invites a user to the workspace. An example can be found in Book2.xlsx.
The input file for this script can be put together by adding the correct E-Mail addresses to the output file of the first script.

This script follow this workflow:
1. It creates the support@leanix.net permission for a workspace
2. It then creates a new API Token in this workspace and authenticates again
3. It then performs a quick GraphQL query to check if certain services ran successfully
4. Lastly, it invites the new user to the workspace

This script implements logging the same way as the first script does. 


To monitor the status of each script, there is detailed and colored outputs for each entry processed.

## Prerequisites
To alter the script to your need, please change the mappings present in each script and add your different API Tokens for the different regions (SUPERADMIN and created by support@leanix.net!).