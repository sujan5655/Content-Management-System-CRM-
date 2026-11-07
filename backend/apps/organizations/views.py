from django.shortcuts import render
from rest_framework.views import APIView, Response

from apps.memberships.models import Membership
from apps.organizations.models import Organization
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.memberships.models import Membership
from apps.organizations.models import Organization


class MyOrganizationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        memberships = (
            Membership.objects
            .select_related("organization")
            .filter(
                user=request.user,
                status=Membership.Status.ACTIVE,
                organization__status=Organization.Status.ACTIVE
            )
            .order_by("organization__name")
        )

        organizations = []

        for membership in memberships:
            organization = membership.organization

            organizations.append({
                "id": str(organization.id),
                "name": organization.name,
                "slug": organization.slug,
                "email": organization.email,
                "role": membership.role,
                "membership_id": str(membership.id)
            })

        return Response(
            {
                "organizations": organizations
            },
            status=status.HTTP_200_OK
        )
