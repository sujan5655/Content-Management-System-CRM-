from django.db import connection
from django.shortcuts import render

# Create your views here.
from django.core.exceptions import ValidationError as DjangoValidationError

from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from apps.memberships.serializers import InvitationAcceptSerializer
from apps.memberships.services.acceptance_service import accept_invitation
from apps.memberships.models import Invitation, Membership


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
# should remove when done
#         with connection.cursor() as cursor:
#           cursor.execute("""
#         SELECT
#             current_setting('app.current_user_id', true),
#             current_setting('app.current_organization_id', true)
#     """)

#           database_user_id, database_organization_id = cursor.fetchone()

#         tenant_context_verified = (
#     database_user_id == str(request.user.id)
#     and database_organization_id == str(organization.id)
# )
# 

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
                },
                # "tenant_context_verified": tenant_context_verified,
            },
            status=status.HTTP_200_OK
        )



from apps.memberships.models import Membership

from apps.memberships.permissions import (
    HasActiveOrganization,
    HasOrganizationRole
)

class EmployeeManagementAccessView(APIView):
    permission_classes = [
        HasActiveOrganization,
        HasOrganizationRole
    ]

    allowed_roles = [
        Membership.Role.OWNER,
        Membership.Role.ADMIN
    ]

    def get(self, request):
        return Response(
            {
                "message": "You have permission to manage employees.",
                "organization": request.organization.name,
                "role": request.membership.role
            },
            status=status.HTTP_200_OK
        )


class EmployeeListView(APIView):
    permission_classes=[
        HasActiveOrganization,
        HasOrganizationRole
    ]
    allowed_roles=[
        Membership.Role.OWNER,
        Membership.Role.ADMIN
    ]
    def get(self, request):
        memberships = (
            Membership.objects
            .select_related("user")
            .filter(
                organization=request.organization,
                status__in=[
                    Membership.Status.ACTIVE,
                    Membership.Status.PENDING,
                    Membership.Status.SUSPENDED
                ]
            )
            .exclude(
                role=Membership.Role.OWNER
            )
            .order_by("-created_at")
        )

        employees = []

        for membership in memberships:
            employees.append({
                "membership_id": str(membership.id),
                "user_id": str(membership.user.id),
                "email": membership.user.email,
                "first_name": membership.user.first_name,
                "last_name": membership.user.last_name,
                "role": membership.role,
                "status": membership.status,
                "joined_at": membership.joined_at,
                "created_at": membership.created_at
            })

        return Response({
            "employees": employees,
            "total": len(employees)
        }, status=status.HTTP_200_OK)

class PendingInvitationListView(APIView):
    permission_classes = [
        HasActiveOrganization,
        HasOrganizationRole
    ]

    allowed_roles = [
        Membership.Role.OWNER,
        Membership.Role.ADMIN
    ]

    def get(self, request):
        invitations = (
            Invitation.objects
            .filter(
                organization=request.organization,
                status=Invitation.Status.PENDING
            )
            .order_by("-created_at")
        )

        results = []

        for invitation in invitations:
            results.append({
                "id": str(invitation.id),
                "email": invitation.email,
                "role": invitation.role,
                "status": invitation.status,
                "expires_at": invitation.expires_at,
                "created_at": invitation.created_at
            })

        return Response({
            "invitations": results,
            "total": len(results)
        }, status=status.HTTP_200_OK)


class InvitationRevokeView(APIView):
    permission_classes = [
        HasActiveOrganization,
        HasOrganizationRole
    ]

    allowed_roles = [
        Membership.Role.OWNER
    ]

    def delete(self, request, invitation_id):
        try:
            invitation = Invitation.objects.get(
                id=invitation_id,
                organization=request.organization
            )
        except Invitation.DoesNotExist:
            return Response(
                {"detail": "Invitation not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if invitation.status != Invitation.Status.PENDING:
            return Response(
                {"detail": "Only pending invitations can be revoked."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if invitation.expires_at <= timezone.now():
            invitation.status = Invitation.Status.EXPIRED
            invitation.save(update_fields=["status"])

            return Response(
                {"detail": "This invitation has already expired."},
                status=status.HTTP_400_BAD_REQUEST
            )

        invitation.status = Invitation.Status.REVOKED
        invitation.save(update_fields=["status"])

        return Response(
            {"message": "Invitation revoked successfully."},
            status=status.HTTP_200_OK
        )



from django.db import transaction

from apps.memberships.serializers import (
    EmployeeStatusUpdateSerializer
)

class EmployeeStatusUpdateView(APIView):
    permission_classes = [
        HasActiveOrganization,
        HasOrganizationRole
    ]

    allowed_roles = [
        Membership.Role.OWNER
    ]

    @transaction.atomic
    def patch(self, request, membership_id):
        serializer = EmployeeStatusUpdateSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            membership = (
                Membership.objects
                .select_for_update()
                .get(
    id=membership_id,
    organization=request.organization,
    role__in=[
        Membership.Role.ADMIN,
        Membership.Role.MANAGER,
        Membership.Role.EMPLOYEE
    ],
    status__in=[
        Membership.Status.ACTIVE,
        Membership.Status.SUSPENDED
    ]
)
            )
        except Membership.DoesNotExist:
            return Response(
                {"detail": "Employee membership not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        new_status = serializer.validated_data["status"]

        if membership.status == new_status:
            return Response(
                {"detail": "Employee already has this status."},
                status=status.HTTP_400_BAD_REQUEST
            )

        membership.status = new_status
        membership.save(update_fields=["status"])

        return Response(
            {
                "message": "Employee status updated successfully.",
                "membership": {
                    "id": str(membership.id),
                    "email": membership.user.email,
                    "role": membership.role,
                    "status": membership.status
                }
            },
            status=status.HTTP_200_OK
        )



from apps.memberships.serializers import (
    EmployeeRoleUpdateSerializer
)

class EmployeeRoleUpdateView(APIView):
    permission_classes = [
        HasActiveOrganization,
        HasOrganizationRole
    ]

    allowed_roles = [
        Membership.Role.OWNER
    ]

    @transaction.atomic
    def patch(self, request, membership_id):
        serializer = EmployeeRoleUpdateSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            membership = (
                Membership.objects
                .select_for_update()
                .get(
                    id=membership_id,
                    organization=request.organization,
                    role__in=[
                        Membership.Role.ADMIN,
                        Membership.Role.MANAGER,
                        Membership.Role.EMPLOYEE
                    ]
                )
            )
        except Membership.DoesNotExist:
            return Response(
                {"detail": "Employee membership not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        new_role = serializer.validated_data["role"]

        if membership.role == new_role:
            return Response(
                {"detail": "Employee already has this role."},
                status=status.HTTP_400_BAD_REQUEST
            )

        membership.role = new_role
        membership.save(update_fields=["role"])

        return Response(
            {
                "message": "Employee role updated successfully.",
                "membership": {
                    "id": str(membership.id),
                    "email": membership.user.email,
                    "role": membership.role,
                    "status": membership.status
                }
            },
            status=status.HTTP_200_OK
        )


class EmployeeRemoveView(APIView):
    permission_classes = [
        HasActiveOrganization,
        HasOrganizationRole
    ]

    allowed_roles = [
        Membership.Role.OWNER
    ]

    @transaction.atomic
    def delete(self, request, membership_id):
        try:
            membership = (
                Membership.objects
                .select_for_update()
                .get(
                    id=membership_id,
                    organization=request.organization,
                    role__in=[
                        Membership.Role.ADMIN,
                        Membership.Role.MANAGER,
                        Membership.Role.EMPLOYEE
                    ]
                )
            )
        except Membership.DoesNotExist:
            return Response(
                {"detail": "Employee membership not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if membership.status == Membership.Status.REMOVED:
            return Response(
                {"detail": "Employee has already been removed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        membership.status = Membership.Status.REMOVED
        membership.save(update_fields=["status"])

        return Response(
            {
                "message": "Employee removed from the organization successfully.",
                "membership": {
                    "id": str(membership.id),
                    "email": membership.user.email,
                    "role": membership.role,
                    "status": membership.status
                }
            },
            status=status.HTTP_200_OK
        )
