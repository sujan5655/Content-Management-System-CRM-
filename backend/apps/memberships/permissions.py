
from uuid import UUID

from rest_framework.permissions import BasePermission

from apps.memberships.models import Membership
from apps.organizations.models import Organization


class HasActiveOrganization(BasePermission):
    message = "You do not have access to this organization."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Organization ID comes from the authenticated JWT
        token = request.auth

        if token is None:
            return False

        organization_id = token.get("organization_id")

        if not organization_id:
            return False

        try:
            organization_id = UUID(str(organization_id))
        except (ValueError, TypeError, AttributeError):
            return False

        membership = (
            Membership.objects
            .select_related("organization")
            .filter(
                user=request.user,
                organization_id=organization_id,
                status=Membership.Status.ACTIVE,
                organization__status=Organization.Status.ACTIVE
            )
            .first()
        )

        if not membership:
            return False

        # Attach verified tenant context to this request
        request.organization = membership.organization
        request.membership = membership

        return True
