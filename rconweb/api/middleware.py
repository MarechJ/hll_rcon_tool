import logging
import os

from django.http import JsonResponse

logger = logging.getLogger("rconweb")


class ServerAccessMiddleware:
    """
    Middleware that checks if the user has permission to access the current server.
    
    This middleware verifies that:
    1. The user is authenticated
    2. If the user has server-specific permissions configured, they must have
       permission for the current server number
    3. Superusers always have access to all servers
    
    Returns a 403 Forbidden response if the user doesn't have access.
    """
    
    # Paths that should be excluded from server access checks
    EXCLUDED_PATHS = [
        '/admin/',  # Django admin should always be accessible
        '/api/login',  # Login endpoint
        '/api/logout',  # Logout endpoint
        '/api/is_logged_in',  # Check login status
        '/api/get_version',  # Public version info
        '/api/get_public_info',  # Public server info
        '/static/',  # Static files
    ]

    # Paths that are allowed even without server access
    # These are needed for the error page to function properly
    ALLOWED_WITHOUT_SERVER_ACCESS = [
        '/api/get_server_list',  # Server list - needed to redirect users to allowed servers
        '/api/get_own_user_permissions',  # User permissions - needed for auth flow
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Check if this path should be excluded from server access checks
        if self._should_exclude_path(request.path):
            return self.get_response(request)
        
        # Only check for authenticated users
        if not request.user or not request.user.is_authenticated:
            return self.get_response(request)
        
        # Superusers always have access
        if request.user.is_superuser:
            return self.get_response(request)
        
        # Get the current server number from environment
        try:
            current_server_number = int(os.getenv("SERVER_NUMBER", "1"))
        except (ValueError, TypeError):
            logger.error("Invalid SERVER_NUMBER environment variable")
            current_server_number = 1
        
        # Import here to avoid circular imports
        from .models import UserServerPermission
        
        # Check if user has any server-specific permissions configured
        user_permissions = UserServerPermission.objects.filter(user=request.user)

        if user_permissions.exists():
            # User has specific server permissions configured
            # Check if they have permission for this server
            allowed_server_numbers = set(
                perm.server_number for perm in user_permissions
            )

            if current_server_number not in allowed_server_numbers:
                # Check if this is an allowed path even without server access
                if self._is_allowed_without_server_access(request.path):
                    # Allow the request to proceed, but the endpoint itself will filter results
                    return self.get_response(request)

                logger.warning(
                    f"User {request.user.username} attempted to access server {current_server_number} "
                    f"via {request.path} but only has permission for servers: {allowed_server_numbers}"
                )

                # Return JSON response for API calls
                if request.path.startswith('/api/'):
                    error_message = (
                        f"You do not have permission to access server {current_server_number}. "
                        f"You only have access to servers: {sorted(allowed_server_numbers)}. "
                        f"Contact an administrator if you believe this is an error."
                    )
                    return JsonResponse(
                        {
                            "result": None,
                            "command": request.path.replace('/api/', ''),
                            "failed": True,
                            "error": error_message,
                            "text": error_message,  # For frontend error display
                            "message": error_message,  # Alternative field
                            "server_number": current_server_number,
                            "allowed_servers": sorted(allowed_server_numbers),
                        },
                        status=403,
                    )
                else:
                    # Return HTML response for non-API calls
                    from django.http import HttpResponseForbidden
                    return HttpResponseForbidden(
                        f"<h1>Access Denied</h1>"
                        f"<p>You do not have permission to access server {current_server_number}.</p>"
                        f"<p>You only have access to servers: {sorted(allowed_server_numbers)}.</p>"
                        f"<p>Contact an administrator if you believe this is an error.</p>"
                    )
        
        # User has no specific permissions configured (can access all servers)
        # or has permission for this server
        return self.get_response(request)
    
    def _should_exclude_path(self, path):
        """Check if the path should be excluded from server access checks."""
        for excluded_path in self.EXCLUDED_PATHS:
            if path.startswith(excluded_path):
                return True
        return False

    def _is_allowed_without_server_access(self, path):
        """Check if the path is allowed even without server access."""
        for allowed_path in self.ALLOWED_WITHOUT_SERVER_ACCESS:
            if path.startswith(allowed_path):
                return True
        return False

