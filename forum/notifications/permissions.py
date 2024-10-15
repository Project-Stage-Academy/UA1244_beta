from rest_framework.permissions import BasePermission

class IsInvestor(BasePermission):
    """
    Permission class to check if the user is an investor.
    """

    def has_permission(self, request, view):
        return request.user.roles.filter(name='investor').exists()
    

class IsStartup(BasePermission):
    """
    Permission class to check if the user is a startup.
    """

    def has_permission(self, request, view):
        return request.user.roles.filter(name='startup').exists()
