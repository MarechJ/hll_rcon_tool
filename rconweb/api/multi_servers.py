import requests
import logging
from functools import wraps
import json
from rcon.utils import ApiKey
from .auth import login_required, api_response
from .utils import _get_data
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger('rcon')

@login_required
@csrf_exempt
def get_server_list(request):
    api_key = ApiKey()
    keys = api_key.get_all_keys()
    my_key = api_key.get_key()

    logger.debug(keys)
    names = []
    for host, key in keys.items():
        if key == my_key:
            continue
        try:
            res = requests.get(f'http://{host}/api/get_connection_info', cookies=dict(sessionid=request.COOKIES.get('sessionid')))
        except requests.exceptions.RequestException:
            logger.warning(f"Unable to connect with {host}")
        if res.ok:
            names.append(res.json()['result'])
    
    return api_response(names)
        

def forward_request(request):
    api_key = ApiKey()
    keys = api_key.get_all_keys()
    my_key = api_key.get_key()

    results = []
    for host, key in keys.items():
        if key == my_key:
            continue
        try:
            url = f'http://{host}{request.path}'
            
            params = dict(request.GET)
            params.pop('forward', None)
            try:
                data = json.loads(request.body)
                data.pop('forward', None)
            except json.JSONDecodeError:
                data = None
            logger.info("Forwarding request: %s %s %s", url, params, data)
            res = requests.get(url, params=params, json=data, cookies=dict(sessionid=request.COOKIES.get('sessionid')))
        except requests.exceptions.RequestException:
            logger.warning(f"Unable to connect with {host}")
        if res.ok:
            results.append({'host': host,'response': res.json()})
    
    return results


""" def forwardable_requet(func):
    def wrapper(request, *args, **kwargs):
        data = _get_data(request)
        
        others = None
        res = func(request, *args, **kwargs)
        if data.get('forward'):
            try:
                others = forward_request(request)
            except: 
                logger.exception("Unexpected error while forwarding request")
            res. """