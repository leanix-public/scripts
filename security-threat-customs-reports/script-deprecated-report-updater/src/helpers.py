from time import time
from datetime import datetime

def get_job_filename_prefix (asset_id: str) -> str:
    now = time()
    prefix = datetime.fromtimestamp(now).strftime('%Y%m%d_%H%M%S')
    return '{prefix}_{asset_id}'.format(prefix=prefix, asset_id=asset_id)
