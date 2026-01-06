# middleware.py
from django.shortcuts import redirect


class RoleBasedRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'role'):
            role = request.user.role
            path = request.path

            if role == 'super_admin':
                if path.startswith('/restaurant_admin/') or path.startswith('/branch_admin/'):
                    return redirect('/super_admin/')

            elif role == 'restaurant_admin':
                if path.startswith('/super_admin/') or path.startswith('/branch_admin/'):
                    return redirect('/restaurant_admin/')

            elif role == 'branch_admin':
                if path.startswith('/super_admin/') or path.startswith('/restaurant_admin/'):
                    return redirect('/branch_admin/')

        return self.get_response(request)