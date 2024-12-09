updateDocuments script

This script lets you update documents.  

Before using this script you update ITComponent relations:
- API-Token
- The instance of your workspace
- The name of your input file 

LeanIX_ID_SPV is the source id and LeanIX_ID_LS is the destination id.

Run the script with the following command:  
```bash
LEANIX_API_TOKEN=<your token> LEANIX_SUBDOMAIN=<your domain> IMPORT_FILE=<your input file> python import.py
```

After running the script, follow the instructions on screen