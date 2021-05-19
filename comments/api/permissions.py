from rest_framework.permissions import BasePermission

class IsObjectOwner(BasePermission):
    """
    checks if the request user is the same user who posted the object
    """
    message = "You do not have permission to access this object"

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user