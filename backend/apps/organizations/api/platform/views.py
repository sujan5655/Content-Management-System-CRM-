from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.accounts.permissions import IsPlatformAdmin

from apps.organizations.api.platform.serializers import (
    OrganizationCreateSerializer
)

from apps.organizations.services.organization_service import (
    create_organization_with_owner_invitation
)


class PlatformOrganizationCreateView(APIView):

    permission_classes = [IsPlatformAdmin]

    def post(self, request):

        serializer = OrganizationCreateSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return Response(
                {
                    "success": False,
                    "message": "Invalid organization details.",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            organization, invitation, raw_token = (
    create_organization_with_owner_invitation(
        name=serializer.validated_data["name"],
        slug=serializer.validated_data["slug"],
        description=serializer.validated_data.get("description", ""),
        email=serializer.validated_data.get("email", ""),
        owner_email=serializer.validated_data["owner_email"],
        superadmin=request.user
    )
)

            activation_url = (
                f"{settings.FRONTEND_URL}/activate"
                f"?token={raw_token}"
            )

            send_mail(
                subject="Activate your CRM Owner account",
                message=(
                    f"You have been invited to manage "
                    f"{organization.name}.\n\n"
                    f"Activate your account using this link:\n"
                    f"{activation_url}\n\n"
                    f"This invitation expires in 48 hours."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[invitation.email],
                fail_silently=False
            )

        except DjangoValidationError as exc:

            return Response(
                {
                    "success": False,
                    "message": "Organization creation failed.",
                    "errors": exc.messages
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "success": True,
                "message": "Organization created and owner invitation sent.",
                "data": {
                    "organization": {
                        "id": str(organization.id),
                        "name": organization.name,
                        "slug": organization.slug,
                        "status": organization.status
                    },
                    "invitation": {
                        "id": str(invitation.id),
                        "email": invitation.email,
                        "role": invitation.role,
                        "status": invitation.status,
                        "expires_at": invitation.expires_at
                    }
                }
            },
            status=status.HTTP_201_CREATED
        )