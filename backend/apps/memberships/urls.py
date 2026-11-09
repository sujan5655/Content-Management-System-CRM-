from django.urls import path

from apps.memberships.views import CurrentOrganizationView, EmployeeInvitationCreateView, EmployeeListView, EmployeeManagementAccessView, EmployeeRemoveView, EmployeeRoleUpdateView, EmployeeStatusUpdateView, InvitationAcceptView, InvitationRevokeView, PendingInvitationListView, SelectOrganizationView
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


path(
    "employee-management-access/",
    EmployeeManagementAccessView.as_view(),
    name="employee-management-access"
),

path(
    "employees/",
    EmployeeListView.as_view(),
    name="employee-list"
),

path(
    "pending-invitations/",
    PendingInvitationListView.as_view(),
    name="pending-invitation-list"
),

path(
    "invitations/<uuid:invitation_id>/revoke/",
    InvitationRevokeView.as_view(),
    name="invitation-revoke"
),

path(
    "employees/<uuid:membership_id>/status/",
    EmployeeStatusUpdateView.as_view(),
    name="employee-status-update"
),
path(
    "employees/<uuid:membership_id>/role/",
    EmployeeRoleUpdateView.as_view(),
    name="employee-role-update"
),

path(
    "employees/<uuid:membership_id>/remove/",
    EmployeeRemoveView.as_view(),
    name="employee-remove"
),
]