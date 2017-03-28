import sys
sys.path.append("..")

from utils import httputil



def ss_send_request(ip, port, data, timeout = 1):
    data["type"] = "request"
    raw_data = json.dump(data)
    return http_send_post(self._master.ip, self._master.port, raw_data, timeout)
    

def ss_creat_reponse(data):
    data["type"] = "response"
    raw_data = json.dump(data)
    return raw_data