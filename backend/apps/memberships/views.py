from django.shortcuts import render

# Create your views here.
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from apps.memberships.serializers import InvitationAcceptSerializer
from apps.memberships.services.acceptance_service import accept_invitation
from apps.memberships.models import Membership


class InvitationAcceptView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = InvitationAcceptSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user, membership = accept_invitation(
                token=serializer.validated_data["token"],
                email=serializer.validated_data["email"],
                first_name=serializer.validated_data["first_name"],
                last_name=serializer.validated_data["last_name"],
                password=serializer.validated_data["password"]
            )

        except DjangoValidationError as exc:
            return Response(
                {"detail": exc.messages},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message": "Invitation accepted successfully. You can now log in.",
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name
                },
                "membership": {
                    "id": str(membership.id),
                    "organization_id": str(membership.organization_id),
                    "role": membership.role,
                    "status": membership.status
                }
            },
            status=status.HTTP_201_CREATED
        )


from django.conf import settings
from django.core.mail import send_mail
from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated

from apps.organizations.models import Organization
from apps.memberships.serializers import EmployeeInvitationCreateSerializer
from apps.memberships.services.invitation_service import create_invitation


class EmployeeInvitationCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, organization_id):
        serializer = EmployeeInvitationCreateSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        organization = get_object_or_404(
            Organization,
            id=organization_id
        )

        try:
            invitation, raw_token = create_invitation(
                organization=organization,
                email=serializer.validated_data["email"],
                role=serializer.validated_data["role"],
                invited_by=request.user
            )

            activation_url = (
                f"{settings.FRONTEND_URL}/activate?token={raw_token}"
            )

            send_mail(
                subject=f"Invitation to join {organization.name}",
                message=(
                    f"You have been invited to join {organization.name}.\n\n"
                    f"Role: {invitation.role}\n\n"
                    f"Accept your invitation using this link:\n"
                    f"{activation_url}\n\n"
                    "This invitation expires in 48 hours."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[invitation.email],
                fail_silently=False
            )

        except DjangoValidationError as exc:
            return Response(
                {"detail": exc.messages},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message": "Employee invitation sent successfully.",
                "invitation": {
                    "id": str(invitation.id),
                    "email": invitation.email,
                    "role": invitation.role,
                    "status": invitation.status,
                    "expires_at": invitation.expires_at
                }
            },
            status=status.HTTP_201_CREATED
        )


from rest_framework_simplejwt.tokens import RefreshToken

from apps.memberships.serializers import OrganizationSelectionSerializer

class SelectOrganizationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrganizationSelectionSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        organization_id = serializer.validated_data["organization_id"]

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
            return Response(
                {
                    "detail": "You do not have an active membership in this organization."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Generate a new JWT pair
        refresh = RefreshToken.for_user(request.user)

        # Attach the selected organization to the JWT
        refresh["organization_id"] = str(membership.organization_id)
        refresh["membership_id"] = str(membership.id)
        refresh["role"] = membership.role

        access = refresh.access_token

        return Response(
            {
                "message": "Organization selected successfully.",
                "organization": {
                    "id": str(membership.organization.id),
                    "name": membership.organization.name,
                    "role": membership.role
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(access)
                }
            },
            status=status.HTTP_200_OK
        )



from rest_framework_simplejwt.tokens import RefreshToken

from apps.memberships.serializers import OrganizationSelectionSerializer
 
class SelectOrganizationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrganizationSelectionSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        organization_id = serializer.validated_data["organization_id"]

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
            return Response(
                {
                    "detail": "You do not have an active membership in this organization."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Generate a new JWT pair
        refresh = RefreshToken.for_user(request.user)

        # Attach the selected organization to the JWT
        refresh["organization_id"] = str(membership.organization_id)
        refresh["membership_id"] = str(membership.id)
        refresh["role"] = membership.role

        access = refresh.access_token

        return Response(
            {
                "message": "Organization selected successfully.",
                "organization": {
                    "id": str(membership.organization.id),
                    "name": membership.organization.name,
                    "role": membership.role
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(access)
                }
            },
            status=status.HTTP_200_OK
        )





from apps.memberships.permissions import HasActiveOrganization
class CurrentOrganizationView(APIView):
    permission_classes = [HasActiveOrganization]

    def get(self, request):
        organization = request.organization
        membership = request.membership

        return Response(
            {
                "organization": {
                    "id": str(organization.id),
                    "name": organization.name,
                    "slug": organization.slug,
                    "email": organization.email,
                    "status": organization.status
                },
                "membership": {
                    "id": str(membership.id),
                    "role": membership.role,
                    "status": membership.status
                },
                "user": {
                    "id": str(request.user.id),
                    "email": request.user.email
                }
            },
            status=status.HTTP_200_OK
        )