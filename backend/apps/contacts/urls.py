from django.urls import path
from apps.contacts.views import ContactDetailView, ContactListCreateView

urlpatterns = [
    path(
        "",
        ContactListCreateView.as_view(),
        name="contact-list-create"
    ),

   

    path(
        "<uuid:contact_id>/",
        ContactDetailView.as_view(),
        name="contact-detail"
    ),
]
