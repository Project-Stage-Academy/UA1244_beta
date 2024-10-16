from rest_framework.permissions import BasePermission
import logging

logger = logging.getLogger(__name__)


class IsAdmin(BasePermission):
    """
    Custom permission class to check if the user is an admin.

    Methods:
        has_permission(request, view): 
            Checks whether the authenticated user has the 'admin' role.

    Returns:
        bool: True if the user is authenticated and has the 'admin' role, False otherwise.
    """
    
    def has_permission(self, request, view):
        """
        Determines if the user is authenticated and has the 'admin' role.

        Args:
            request (Request): The HTTP request object containing user information.
            view (View): The view being accessed.

        Returns:
            bool: True if the user is authenticated and has the 'admin' role, False otherwise.
        """
        is_admin = request.user and request.user.is_authenticated and request.user.roles.filter(name='admin').exists()

        if not is_admin:
            logger.warning(f"Permission denied for user {request.user}")
        else:
            logger.info(f"User '{request.user.username}' granted access to '{view.name}' as admin.")
        return is_admin


class IsOwner(BasePermission):
    """
    Custom permission class to check if the user is the owner of the object.

    Methods:
        has_object_permission(request, view, obj): 
            Checks if the user owns the object being accessed.

    Returns:
        bool: True if the user is the owner of the object, False otherwise.
    """

    def has_object_permission(self, request, view, obj):
        """
        Determines if the user is the owner of the object.

        Args:
            request (Request): The HTTP request object containing user information.
            view (View): The view being accessed.
            obj (Object): The object being accessed.

        Returns:
            bool: True if the user is the owner of the object, False otherwise.
        """
        return obj == request.user


class IsInvestor(BasePermission):
    """
    Custom permission class for users with the active role 'investor'.

    Methods:
        has_permission(request, view): 
            Checks if the authenticated user has 'investor' as their active role.

    Returns:
        bool: True if the user is authenticated and their active role is 'investor', False otherwise.
    """

    def has_permission(self, request, view):
        """
        Determines if the user has 'investor' as their active role.

        Args:
            request (Request): The HTTP request object containing user information.
            view (View): The view being accessed.

        Returns:
            bool: True if the user's active role is 'investor', False otherwise.
        """
        if request.user.is_authenticated:
            return request.user.active_role and request.user.active_role.name == 'investor'
        return False


class IsStartup(BasePermission):
    """
    Custom permission class for users with the active role 'startup'.

    Methods:
        has_permission(request, view): 
            Checks if the authenticated user has 'startup' as their active role.

    Returns:
        bool: True if the user is authenticated and their active role is 'startup', False otherwise.
    """

    def has_permission(self, request, view):
        """
        Determines if the user has 'startup' as their active role.

        Args:
            request (Request): The HTTP request object containing user information.
            view (View): The view being accessed.

        Returns:
            bool: True if the user's active role is 'startup', False otherwise.
        """
        if request.user.is_authenticated:
            return request.user.active_role and request.user.active_role.name == 'startup'
        return False
        
        if obj == request.user:
            logger.info(f"User '{request.user.username}' has permission to access object '{obj}' as the owner.")
            return True
        else:
            logger.warning(
                f"User '{request.user.username}' denied access to object '{obj}' due to insufficient permissions.")
            return False
