from rest_framework.permissions import BasePermission

class IsSuperAdmin(BasePermission):
    message = 'You are not Super Admin'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'super_admin'


class IsRestaurantAdmin(BasePermission):
    message = 'You are not Restaurant Admin'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'restaurant_admin'


class IsBranchAdmin(BasePermission):
    message = 'You are not Branch Admin'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'branch_admin'


class IsUser(BasePermission):
    message = 'You are not User'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'user'
