# script-custom-report-updater
A script for globally upgrading a Custom Report from a "bundle.tgz" file.
It is intended to be used as an emergency alternative in case that a critical security flaw is identified for
a published asset id (i.e. report version) on the store.

## How does it work:
1. Clone this project from the repo and install the dependencies using the `npm install` command. (PS: yes, this is a python project that uses npm...)
2. Create an `.env` file at the root of this project containg the following entries: USERNAME, PASSWORD, REPORT_STORE_ID (e.g. the report UUID), and the REPORT_ID (e.g. net.leanix.report.test). Keep in mind that the credentials must be of an user that is superadmin). This `.env` file must never be commited to the repo in any circumstances!!!
3. Drop the updated "bundle.tgz" file in the project root folder. Do not forget this step!
4. Drop the sqlite file exported from torg (containing the installs table) also on the project root folder. This file should be named "torg.sqlite". Do not forget this step!
5. Run the script by executing the `npm start` command and watch the magic happen (you can also start a python debug session on main.py using vscode).
6. Inspect the job logs in the `./logs` folder.

## Notes:
1. Again, if you are using VSCode, then you can also start a debug session using the `main.py` file as entrypoint.
2. Bearer token expiration time is 3600s (1 hour). If you observe 401 errors during the execution, delete the `./data/bearerIndex.json` file and run the script again.

## Questions:
#team-pixel
paulo.santos@leanix.net