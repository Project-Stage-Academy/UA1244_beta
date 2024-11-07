"""
Custom permissions for notifications app.

This module provides custom permissions to restrict access to resources
based on the user's roles, specifically checking for 'investor' or 'startup' roles.
"""

from rest_framework.permissions import BasePermission

class IsInvestorOrStartup(BasePermission):
    """
    Custom permission to allow access to users who are either investors or startups.
    """

    def has_permission(self, request, view):
        """
        Checks if the user has 'investor' or 'startup' role.
        """
        return request.user and (
            request.user.roles.filter(name='investor').exists() or 
            request.user.roles.filter(name='startup').exists()
        )

    def has_object_permission(self, request, view, obj):
        """
        Checks if the object is related to the user's investor or startup profile.
        """
        return (
            hasattr(request.user, 'investor') and obj.investor == request.user.investor or
            hasattr(request.user, 'startup') and obj.startup == request.user.startup
        )
