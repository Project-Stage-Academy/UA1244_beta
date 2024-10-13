from rest_framework.permissions import BasePermission
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
        return request.user and request.user.is_authenticated and request.user.roles.filter(name='admin').exists()


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
        return obj == request.user
    


from rest_framework.permissions import BasePermission

class IsInvestor(BasePermission):
    """
    Дозвіл тільки для користувачів з активною роллю 'investor'.
    """
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.active_role and request.user.active_role.name == 'investor'
        return False

class IsStartup(BasePermission):
    """
    Дозвіл тільки для користувачів з активною роллю 'startup'.
    """
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.active_role and request.user.active_role.name == 'startup'
        return False