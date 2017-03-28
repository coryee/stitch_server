import __init__
from utils import httputil



def ss_send_request(ip, port, data, timeout = 1):
    data["type"] = 0
    raw_data = json.dump(data)
    return httputil.http_send_post(self._master.ip, self._master.port, raw_data, timeout)
    

def ss_creat_reponse(data):
    data["type"] = 1
    raw_data = json.dump(data)
    return raw_data