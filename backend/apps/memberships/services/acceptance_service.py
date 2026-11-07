
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.memberships.models import Invitation, Membership
from apps.memberships.services.invitation_service import hash_invitation_token


User = get_user_model()


@transaction.atomic
def accept_invitation(
    *,
    token,
    email,
    first_name,
    last_name,
    password
):
    # 1. Hash the submitted token
    token_hash = hash_invitation_token(token)

    # 2. Find and lock the invitation
    try:
        invitation = Invitation.objects.select_for_update().get(
            token_hash=token_hash
        )
    except Invitation.DoesNotExist:
        raise ValidationError("Invalid invitation token.")

    # 3. Check invitation status
    if invitation.status != Invitation.Status.PENDING:
        raise ValidationError("This invitation is no longer valid.")

    # 4. Check expiration
    if timezone.now() >= invitation.expires_at:
        raise ValidationError("This invitation has expired.")

    # 5. Verify email
    email = email.strip().lower()

    if email != invitation.email.strip().lower():
        raise ValidationError(
            "Email does not match the invitation."
        )

    # 6. Check organization status
    organization = invitation.organization

    if invitation.role == Membership.Role.OWNER:
        if organization.status != organization.Status.PENDING:
            raise ValidationError(
                "This organization is not awaiting Owner activation."
            )

        existing_owner = Membership.objects.filter(
            organization=organization,
            role=Membership.Role.OWNER,
            status=Membership.Status.ACTIVE
        ).exists()

        if existing_owner:
            raise ValidationError(
                "This organization already has an active Owner."
            )

    elif organization.status != organization.Status.ACTIVE:
        raise ValidationError(
            "This organization is not active."
        )

    # 7. Check whether the user already exists
    user = User.objects.filter(email__iexact=email).first()

    if user and user.is_active:
        raise ValidationError(
            "An active account already exists with this email. "
            "Please use the existing account to accept the invitation."
        )

    # 8. Create or activate the user account
    if user:
        user.first_name = first_name
        user.last_name = last_name
        user.set_password(password)
        user.is_active = True

        user.save(update_fields=[
            "first_name",
            "last_name",
            "password",
            "is_active"
        ])
    else:
        user = User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            is_active=True
        )

    # 9. Create the membership
    membership = Membership.objects.create(
        user=user,
        organization=organization,
        role=invitation.role,
        status=Membership.Status.ACTIVE,
        joined_at=timezone.now()
    )

    # 10. Activate the organization for its Owner
    if invitation.role == Membership.Role.OWNER:
        organization.status = organization.Status.ACTIVE
        organization.save(update_fields=["status"])

    # 11. Mark invitation as accepted
    invitation.status = Invitation.Status.ACCEPTED
    invitation.accepted_at = timezone.now()
    invitation.save(update_fields=[
        "status",
        "accepted_at"
    ])

    return user, membership
