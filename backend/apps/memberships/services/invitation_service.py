
import secrets
import hashlib

from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from apps.memberships.models import Membership, Invitation


def hash_invitation_token(token):
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


@transaction.atomic
def create_invitation(
    *,
    organization,
    email,
    role,
    invited_by,
    expires_in_hours=48
):

    email = email.strip().lower()

    valid_roles = Membership.Role.values

    if role not in valid_roles:
        raise ValidationError("Invalid membership role.")

    # Superadmin can invite an organization owner.
    if role == Membership.Role.OWNER:

        if not invited_by.is_platform_admin:
            raise ValidationError(
                "Only platform administrators can invite owners."
            )

        if organization.status != organization.Status.PENDING:
            raise ValidationError(
                "Owner invitations require a pending organization."
            )

    # Organization owner can invite employees.
    else:

        owner_membership = Membership.objects.filter(
            user=invited_by,
            organization=organization,
            role=Membership.Role.OWNER,
            status=Membership.Status.ACTIVE
        ).exists()

        if not owner_membership:
            raise ValidationError(
                "Only an active organization owner can invite members."
            )

        if organization.status != organization.Status.ACTIVE:
            raise ValidationError(
                "Organization is not active."
            )

    # Prevent duplicate membership.
    existing_membership = Membership.objects.filter(
        organization=organization,
        user__email__iexact=email
    ).exists()

    if existing_membership:
        raise ValidationError(
            "This user already has a membership in this organization."
        )

    # Revoke previous pending invitations.
    Invitation.objects.filter(
        organization=organization,
        email__iexact=email,
        status=Invitation.Status.PENDING
    ).update(
        status=Invitation.Status.REVOKED
    )

    # Generate a secure invitation token.
    raw_token = secrets.token_urlsafe(48)

    token_hash = hash_invitation_token(raw_token)

    invitation = Invitation.objects.create(
        email=email,
        organization=organization,
        role=role,
        token_hash=token_hash,
        invited_by=invited_by,
        expires_at=timezone.now() + timedelta(
            hours=expires_in_hours
        )
    )

    return invitation, raw_token
