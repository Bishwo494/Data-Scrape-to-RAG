import os
import sys


central_home = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(central_home)
print(central_home)

def initialize_json_config():
    import json
    
    global BASE_URL
    global pages_to_scn
    global NESSIE_URI
    global MINIO_ENDPOINT
    global MINIO_ACCESS_KEY
    global MINIO_SECRET_KEY
    global local_vloume
    global minio_bucket

    #config file 
    global CONFIG_FILE
    CONFIG_FILE= central_home +'/notebooks/config/config.json'

    #variables from config
    with open(os.path.abspath(CONFIG_FILE), 'r') as js:
        js_conf = json.load(js)
    
    BASE_URL = js_conf['BASE_URL']
    pages_to_scn = js_conf['pages_to_scn']
    NESSIE_URI = js_conf['NESSIE_URI']
    MINIO_ENDPOINT = js_conf['MINIO_ENDPOINT']
    MINIO_ACCESS_KEY = js_conf['MINIO_ACCESS_KEY']
    MINIO_SECRET_KEY = js_conf['MINIO_SECRET_KEY']
    local_vloume = js_conf['local_vloume']
    minio_bucket = js_conf['minio_bucket']

initialize_json_config()
