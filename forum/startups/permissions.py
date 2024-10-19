from rest_framework.permissions import BasePermission

class IsInvestorOrStartup(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.active_role in ['investor', 'startup']