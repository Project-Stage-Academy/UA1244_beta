from rest_framework.permissions import BasePermission
from rest_framework.permissions import BasePermission

class IsInvestorOrStartup(BasePermission):
    """
    Custom permission to allow access to users who are either investors or startups.
    """

    def has_permission(self, request, view):
        return request.user and (request.user.roles.filter(name='investor').exists() or request.user.roles.filter(name='startup').exists())

    def has_object_permission(self, request, view, obj):
        return obj.investor == request.user.investor or obj.startup == request.user.startup