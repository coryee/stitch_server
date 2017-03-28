import requests
import json



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