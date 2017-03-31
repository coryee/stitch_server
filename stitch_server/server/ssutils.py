import __init__
import json
from utils import httputil



def ss_send_request(ip, port, api, data, timeout = 1):
    data["type"] = 0
    raw_data = json.dumps(data)
    return httputil.http_send_post(ip, port, api, raw_data, timeout)
    

def ss_creat_reponse(data):
    data["type"] = 1
    raw_data = json.dumps(data)
    return raw_data