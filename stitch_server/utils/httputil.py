import __init__
import requests
import json
from errors import ss_err_msgs


def http_send_post(ip, port, data, timeout = 1):
    host = "%s:%d" % (ip, port)
    headers = {'Content-type': 'application/json'}
    r = None
    result = -1
    try:
        response = requests.post(host, headers = headers, data = data, timeout = timeout)
        if response.status_code == requests.codes.ok:
            result = 0
    except requests.exceptions.RequestException as e:
        pass
    
    return (result, response)


def http_creat_reponse(err_code, data={}):
    data["type"] = 1
    data["err_code"] = err_code
    data["err_msg"] = ss_err_msgs.get(err_code, "")
    raw_data = json.dumps(data)
    return raw_data