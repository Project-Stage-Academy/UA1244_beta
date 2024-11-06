import logging
from rest_framework.permissions import BasePermission

logger = logging.getLogger(__name__)


class IsAdmin(BasePermission):
    """
    Custom permission class to check if the user is an admin.
    """

    def has_permission(self, request, view):
        """
        Determines if the user is authenticated and has the 'admin' role.
        """
        is_admin = request.user and request.user.is_authenticated and request.user.roles.filter(name='admin').exists()

        if not is_admin:
            logger.warning("Permission denied for user %s", request.user)
        else:
            logger.info("User '%s' granted access to '%s' as admin.", request.user.username, view.__class__.__name__)
        return is_admin


class IsOwner(BasePermission):
    """
    Custom permission class to check if the user is the owner of the object.
    """

    def has_object_permission(self, request, view, obj):
        """
        Determines if the user is the owner of the object.
        """
        return obj == request.user


class IsInvestor(BasePermission):
    """
    Custom permission class for users with the active role 'investor'.
    """

    def has_permission(self, request, view):
        """
        Determines if the user has 'investor' as their active role.
        """
        if request.user.is_authenticated:
            return request.user.active_role and request.user.active_role.name == 'investor'
        return False


class IsStartup(BasePermission):
    """
    Custom permission class for users with the active role 'startup'.
    """

    def has_permission(self, request, view):
        """
        Determines if the user has 'startup' as their active role.
        """
        if request.user.is_authenticated and request.user.active_role and request.user.active_role.name == 'startup':
            logger.info("User '%s' granted access as a startup.", request.user.username)
            return True

        logger.warning("User '%s' denied access. Startup role required.", request.user.username)
        return False
