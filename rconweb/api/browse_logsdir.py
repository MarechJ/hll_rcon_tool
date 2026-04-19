import os
from datetime import datetime

from django.http import Http404, HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from .auth import login_required
from .decorators import require_http_methods


@csrf_exempt
@login_required()
@user_passes_test(lambda u: u.is_staff)
@require_http_methods(["GET"])
def list_logs(request, path=''):
    """
    Displays a raw list of folders and files in the /logs folder
    """
    root = os.getenv("LOGGING_PATH", "/logs")

    full_path = os.path.normpath(os.path.join(root, path))
    if not full_path.startswith(os.path.normpath(root)) or not os.path.exists(full_path):
        raise Http404("Directory not found")

    if os.path.isfile(full_path):
        from django.views.static import serve
        return serve(request, path, document_root=root)

    try:
        items = []
        for entry in os.scandir(full_path):
            stats = entry.stat()
            items.append({
                'name': entry.name,
                'is_dir': entry.is_dir(),
                'size': stats.st_size,
                'mtime': datetime.fromtimestamp(stats.st_mtime)
            })

        # Sort: directories first, then alphabetical
        items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))

        html = f"<html><head><title>CRCON - logs/{path}</title><style>"
        html += "pre { margin: 0; padding: 2px; }"
        html += "a { text-decoration: none; }"
        html += ".l { display: inline-block; text-decoration: none; color: inherit; }"
        html += ".l:hover { background-color: #f0f0f0; }"
        html += "</style></head><body>"
        html += f"<h1>Index of /api/logs/{path}</h1><hr><pre>"
        html += f"<b>{'Name':<55} {'Size':>12} {'Last Modified':>21}</b><hr>"

        if path:
            html += f"<span class='l'><a href='..'>../</a></span>\n"

        for item in items:
            suffix = '/' if item['is_dir'] else ''
            name = item['name'] + suffix
            date = item['mtime'].strftime('%Y-%m-%d %H:%M:%S')
            size = f"{item['size'] / 1024:.1f} KB" if not item['is_dir'] else "-"
            html += f"<span class='l'><a href='{name}'>{name:<55}</a> {size:>12} {date:>21}</span>\n"

        html += "</pre><hr></body></html>"
        return HttpResponse(html)
    except Exception as e:
        return HttpResponse(f"Error accessing logs: {e}", status=500)
