from dotenv import load_dotenv
from os import environ
from sqlite3 import connect
from auth import build_bearer_token_index
from mtm import get_impersonation_for_workspace, finalize_impersonation_session
from torg import uninstall_asset_version_from_workspace
from pathfinder import build_workspace_reports_index, upload_bundle, enable_asset_version_on_workspace, delete_asset_version_from_workspace
from helpers import get_job_filename_prefix
import logging
from os import path, makedirs
import requests
import tarfile
from json import loads, dump
from packaging.version import Version
import sys

load_dotenv()  # take environment variables from .env.
regions = ['ae', 'au', 'br', 'ca', 'ch', 'de', 'eu', 'uk', 'us']

temp_dir = './.data'
logs_dir = './.logs'
username = environ['USERNAME']
password = environ['PASSWORD']
report_store_id = environ['REPORT_STORE_ID']
report_id = environ['REPORT_ID']

if not path.exists(temp_dir):
    makedirs(temp_dir)
if not path.exists(logs_dir):
    makedirs(logs_dir)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(path.join(logs_dir, get_job_filename_prefix(report_store_id) + '.log')),
        logging.StreamHandler()
    ]
)
logging.root.setLevel(logging.INFO)

# https://stackoverflow.com/questions/3300464/how-can-i-get-dict-from-sqlite-query -> converts enums into dicts
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

report_version = None
filepath = './bundle.tgz'
# used to track progress of a job, for a report_store_id
job_filepath = path.join(temp_dir, '{report_store_id}_job.json'.format(report_store_id=report_store_id))

upgraded_workspace_index = {}
try:
    with open(job_filepath) as f:
        upgraded_workspace_index=loads(f.read())
    logging.info('continuing the job for report_store_id {report_store_id}, {count} workspaces already upgraded'.format(report_store_id=report_store_id, count=len(upgraded_workspace_index)))
except:
    logging.info('starting a new job for report_store_id {report_store_id}'.format(report_store_id=report_store_id))

# check bundle file contents
tar = tarfile.open(filepath, "r:gz")
for member in tar.getmembers():
    if member.name != 'lxreport.json':
        continue
    f=tar.extractfile(member)
    content=loads(f.read())
    if content['id'] != report_id:
        raise Exception('wrong bundle.tgz, expected {report_id}, got {content_id}'.format(report_id=report_id, content_id=content['id']))
    report_version = content['version']
    break
tar.close()

if report_version == None:
    raise Exception('could not find the report version in lxreport.json')

# get report instalations from the database
con = connect('./torg.sqlite')
con.row_factory = dict_factory
cur = con.cursor()
database_installations = cur.execute('SELECT install_id, ws_id, ws_name, instance_url, ws_status, ws_url, ws_region FROM installs WHERE asset_id = ?', [report_store_id]).fetchall()

installations = []
skipped_workspaces = []

for installation in database_installations:
    workspace_id = installation['ws_id']
    if workspace_id in upgraded_workspace_index:
        skipped_workspaces.append(workspace_id)
    else:
        installations.append(installation)

if len(skipped_workspaces) > 0:
    logging.info('skipping {count} workspaces, already upgraded...'.format(count=len(skipped_workspaces)))

if len(installations) == 0:
    logging.info('nothing to do for this job, all workspaces were upgraded')
    sys.exit()

# build our index of bearer tokens, so that we can access into a workspace in any region during the process
token_idx = build_bearer_token_index(regions, username, password, path.join(temp_dir, 'bearerIndex.json'))

total_installations = len(installations)
current_installation = 0

for installation in installations:
    current_installation = current_installation + 1
    region = installation['ws_region']
    workspace_status = installation['ws_status']
    workspace_id = installation['ws_id']

    if workspace_status != 'ACTIVE':
        logging.info('skipping workspace {workspace_id}, region = {region}, status = {status}'.format(workspace_id=workspace_id, region=region, status=workspace_status))
        upgraded_workspace_index[workspace_id] = region
        with open(job_filepath, 'w') as f:
            dump(upgraded_workspace_index, f, indent=4)
        continue

    token = token_idx[region]
    impersonation = None
    attempts = 0
    max_attemps = 2
    while impersonation == None and attempts < max_attemps: # allow 1 retry to compensate for an expired bearer token
        attempts = attempts + 1
        try:
            impersonation = get_impersonation_for_workspace(
                workspace_id=workspace_id,
                region=region,
                token=token,
                reason='script-custom-report-updater: updating report asset_id {report_store_id}'.format(report_store_id=report_store_id)
            )
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 404:
                logging.warning('Seems that workspace {region} {workspace_id} does not exist, please confirm it personally!'.format(region=region.upper(), workspace_id=workspace_id))
                attempts = max_attemps
                continue
            if err.response.status_code == 403:
                logging.warning('Could not login into workspace {region} {workspace_id}, please check it personally!'.format(region=region.upper(), workspace_id=workspace_id))
                attempts = max_attemps
                continue
            if err.response.status_code == 401:
                token_idx = build_bearer_token_index(regions, username, password, path.join(temp_dir, 'bearerIndex.json'), delete_file=True)
            else:
                raise err
        except err:
            logging.warning('could not get impersonation for workspace {workspace_id}, consider refreshing the workspace index, skipping for now...'.format(workspace_id=workspace_id))
            attempts = max_attemps
            continue
    if impersonation == None:
        continue

    try:
        prefix = '{current}/{total} {region} {workspace_id} {workspace_name}'.format(current=current_installation, total=total_installations, region=impersonation['region'], workspace_id=impersonation['workspace_id'], workspace_name=impersonation['workspace_name'])
        logging.info('{prefix}: Logged in'.format(prefix=prefix))

        impersonation_id = impersonation['impersonation_id']
        bearer = impersonation['bearer']

        logging.info('{prefix}: Building reports index...'.format(prefix=prefix))
        workspace_reports_index = build_workspace_reports_index(bearer)
        needs_upgrade = False # We'll only upgrade the report if, at least, one version is enabled/activated in the workspace
        reports_to_be_deleted = [] # We'll delete all the old/obsolete versions for this report
        for report in workspace_reports_index.values():
            if report['reportId'] == report_id and (Version(report['version']) < Version(report_version)):
                logging.info('{prefix}: Found obsolete report {report_id} v{version}, will be removed from workspace.'.format(prefix=prefix,report_id=report_id,version=report['version']))
                if report['enabled'] == True:
                    needs_upgrade = True
                reports_to_be_deleted.append(report['id'])
        if needs_upgrade == True:
            logging.info('{prefix}: Upgrading the report {report_id} v{version}'.format(prefix=prefix, report_id=report_id, version=report_version))
            new_report_id = upload_bundle(filepath=filepath, bearer=bearer)
            workspace_reports_index = build_workspace_reports_index(bearer)
            report = workspace_reports_index[new_report_id]
            logging.info('{prefix}: Enabling the report {report_id} v{version}'.format(prefix=prefix, report_id=report_id, version=report_version))
            enable_asset_version_on_workspace(new_report_id, report, bearer)
        if len(reports_to_be_deleted) > 0:
            logging.info('{prefix}: Uninstalling {count} obsolete report versions...'.format(prefix=prefix, count=len(reports_to_be_deleted)))
        else:
            logging.info('{prefix}: Nothing to on this workspace.'.format(prefix=prefix))
        for report_id_deleted in reports_to_be_deleted:
            uninstall_asset_version_from_workspace(report_id_deleted, bearer)
            delete_asset_version_from_workspace(report_id_deleted, bearer)
        upgraded_workspace_index[workspace_id] = region
        with open(job_filepath, 'w') as f:
            dump(upgraded_workspace_index, f, indent=4)
    finally:
        finalize_impersonation_session(impersonation_id, region, token_idx) # finalize the impersonation session on mtm
        logging.info('{prefix}: Logged out'.format(prefix=prefix))
   
