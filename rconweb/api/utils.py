import json

def _get_data(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.GET
    return data
