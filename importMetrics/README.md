importMetrics script

This script lets you import Metrics from either a csv or a xlsx file.  

Before using this script you will need the following information:
- API-Token
- The instance of your workspace
- Name and filetype of you input-file

Run the script with the following command:  
```bash
LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> IMPORT_FILE=<your input file> python importMetrics.py
```