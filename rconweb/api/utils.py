import json
from functools import wraps


def _get_data(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.GET
    return data


def allow_csv(endpoint):
    @wraps(endpoint)
    def wrapper(request, *args, **kwargs):
        to_csv = _get_data(request).get("to_csv")
        res = endpoint(request, *args, **kwargs)
        
