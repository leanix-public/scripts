## Description
This script loads relations and their attributes from one or many Excel files in the standard LeanIX Excel Import/Export Format.
A file of Un-Matched records is exported as NonMatchRecords.xlsx

### Dependencies

Python 3

Modules: pandas,requests, json, time, os

### Executing program


* Generate an API Token in your LeanIX Workspace and assign it to the "api_token" field in configs.json
* Determine the region on which your LeanIX instance is hosted (us, eu, ca, au) add this value to the 'region' field in configs.json
* Determine the domain of your LeanIX instance. This can be found in the first part the url in your browser when you navigate to LeanIX (typically, 'mcompany.leanix.net'). Add it to the "domain" attribute in configs.json.
* If your files include date fields to be imported, add the name(s) of the field(s) to the "date_fields" array in configs.json. This name can be pulled directly from the first row of your formatted Excel file. 
* Place your formatted Excel files in the 'run_files' directory
* Run script by command line 'python3 run.py'
