To initiate Integration API runs witht his script:

1) Clone the repository to your local desired environment. 

2) Populate the configs.xlsx file with the details of your LeanIX iAPI connectors
Note: You can include multiple connectors by adding multiple rows of configurations

3) Generate an API Token in Leanix Admin > API Tokens

4) Open a Command Line Interface session at the level of your local copy of the script. 

5) Initiate a run in the CLI by adapting and executing the follwing command:

python startOutboundRun.py start-run --api-token <your api token> --app-instance <your app instance> --svc-instance <your svc instance>

Note: Details about these parameters can be found in the tutorial documentation https://dev.leanix.net/docs/managing-integration-api-runs-with-python
