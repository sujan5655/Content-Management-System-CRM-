from django.urls import path

from apps.memberships.views import CurrentOrganizationView, EmployeeInvitationCreateView, InvitationAcceptView, SelectOrganizationView
from apps.organizations.views import MyOrganizationsView


urlpatterns = [
    path(
        "accept-invitation/",
        InvitationAcceptView.as_view(),
        name="accept-invitation"
    ),
 path(
        "organizations/<uuid:organization_id>/invitations/",
        EmployeeInvitationCreateView.as_view(),
        name="employee-invitation-create"
    ),

    path(
    "my-organizations/",
    MyOrganizationsView.as_view(),
    name="my-organizations"
),

path(
    "select-organization/",
    SelectOrganizationView.as_view(),
    name="select-organization"
),


path(
    "current-organization/",
    CurrentOrganizationView.as_view(),
    name="current-organization"
),

]