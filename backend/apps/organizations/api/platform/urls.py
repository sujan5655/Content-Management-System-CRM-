from django.urls import path

from .views import PlatformOrganizationCreateView


urlpatterns = [
    path(
        "organizations/",
        PlatformOrganizationCreateView.as_view(),
        name="platform-organization-create"
    ),
]