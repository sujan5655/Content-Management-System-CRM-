from rest_framework.permissions import BasePermission


class IsPlatformAdmin(BasePermission):

    message = "Platform administrator access required."

    def has_permission(self, request, view):

        user = request.user

        return (
            user
            and user.is_authenticated
            and user.is_active
            and user.is_platform_admin
            and user.is_superuser
        )