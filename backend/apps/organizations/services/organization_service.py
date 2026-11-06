from django.db import transaction
from django.core.exceptions import ValidationError

from apps.organizations.models import Organization
from apps.memberships.models import Membership
from apps.memberships.services.invitation_service import (
    create_invitation
)

@transaction.atomic
def create_organization_with_owner_invitation(
    *,
    name,
    slug,
    description,
    email,
    owner_email,
    superadmin
):
    if (
        not superadmin.is_active
        or not superadmin.is_platform_admin
        or not superadmin.is_superuser
    ):
        raise ValidationError("Platform administrator access required.")

    if Organization.objects.filter(slug=slug).exists():
        raise ValidationError("Organization slug already exists.")

    organization = Organization.objects.create(
        name=name,
        slug=slug,
        description=description,
        email=email,
        status=Organization.Status.PENDING
    )

    invitation, raw_token = create_invitation(
        organization=organization,
        email=owner_email,
        role=Membership.Role.OWNER,
        invited_by=superadmin
    )

    return organization, invitation, raw_token