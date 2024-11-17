
import json
import requests
from constants import *
from biot_python_sdk.BioT_API_URLS import *

def get_access_token(username,password,env):
    login_data = {"username": username,"password": password}
    headers = {"Accept": "application/json",
                "Content-Type": "application/json; charset=utf-8",
                "Content-Length": str(len(json.dumps(login_data))),
                "User-Agent": USER_AGENT}
    if env == 'development':
        BASE_URL= DEV_BASE_URL
    elif env=='production':
        BASE_URL = PROD_BASE_URL
    else:
        raise Exception('env input is not correct.')
    response = requests.post(BASE_URL + LOGIN_SUB_URL, headers=headers, json=login_data)
    response_content_dict =json.loads(response.content)
    access_token=response_content_dict['accessJwt']['token']
    return access_token