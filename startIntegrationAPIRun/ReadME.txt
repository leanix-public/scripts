This script can be used to initiate an inbound or outbound run of the Integration API. Test LDIFs and Connectors are included in this repository as well, but you can of course leverage your own connectors and LDIF data. If you DO want to use the sample data, you will have to configure the appropriate connectors in your Leanix workspace. 

Note: connectorType, connectorId, connectorVersion, lxVersion, processingDirection, and processingMode parameters need to match exactly with their corresponding Connector config values in LeanIX.

To initiate an Integration API run with this script:

1) Clone the repository to your local environment. 

2) Generate an API Token in Leanix Admin > API Tokens and add it to the access.json file

3) Add your unique domain to the access.json file (Note: This is the first part of your leanix workspace url)

4) Initiate a run in the CLI by adapting and executing the follwing command:

python callIntegrationAPI.py run-integration-api --ldif-filename <your-ldif-filename.json>

