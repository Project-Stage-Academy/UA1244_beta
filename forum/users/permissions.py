from rest_framework.permissions import BasePermission
import logging

logger = logging.getLogger(__name__)


class IsAdmin(BasePermission):
    """
    Custom permission to check if the user is an admin.

    Methods:
        has_permission(request, view): Determines whether the user has permission to access the view.
            Returns True if the user is authenticated and has the role 'admin'.
    """

    def has_permission(self, request, view):
        """
        Check if the user is authenticated and has the role 'admin'.

        Args:
            request (Request): The HTTP request object containing user information.
            view (View): The view that is being accessed.

        Returns:
            bool: True if the user is authenticated and has the role 'admin', False otherwise.
        """
        is_admin = request.user and request.user.is_authenticated and request.user.roles.filter(name='admin').exists()

        if not is_admin:
            logger.warning(f"Permission denied for user {request.user}")
        else:
            logger.info(f"User '{request.user.username}' granted access to '{view.name}' as admin.")
        return is_admin


class IsOwner(BasePermission):
    """
    Custom permission to check if the user is the owner of the object.

    Methods:
        has_object_permission(request, view, obj): Determines whether the user has permission to access the specific object.
            Returns True if the user is the owner of the object.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if the user is the owner of the object.

        Args:
            request (Request): The HTTP request object containing user information.
            view (View): The view that is being accessed.
            obj (Object): The object that is being accessed.

        Returns:
            bool: True if the user is the owner of the object, False otherwise.
        """
        if obj == request.user:
            logger.info(f"User '{request.user.username}' has permission to access object '{obj}' as the owner.")
            return True
        else:
            logger.warning(
                f"User '{request.user.username}' denied access to object '{obj}' due to insufficient permissions.")
            return False
