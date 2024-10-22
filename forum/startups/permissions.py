from rest_framework.permissions import BasePermission

class IsInvestorOrStartup(BasePermission):
    """
    Custom permission to grant access only to authenticated users
    who have an active role of either 'investor' or 'startup'.

    This permission checks whether the user is logged in (`is_authenticated`)
    and whether their `active_role` attribute is either 'investor' or 'startup'.
    
    Returns:
        bool: True if the user is authenticated and has the role of 'investor' 
        or 'startup', otherwise False.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.active_role in ['investor', 'startup']