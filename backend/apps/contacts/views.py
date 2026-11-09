from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.contacts.models import Contact
from apps.contacts.serializers import ContactSerializer
from apps.memberships.permissions import HasActiveOrganization


class ContactListCreateView(APIView):

    permission_classes = [HasActiveOrganization]

    def get(self, request):

        contacts = Contact.objects.filter(
            organization=request.organization
        )

        serializer = ContactSerializer(
            contacts,
            many=True
        )

        return Response(serializer.data)

    def post(self, request):

        serializer = ContactSerializer(
            data=request.data
        )

        if serializer.is_valid():

            serializer.save(
                organization=request.organization,
                created_by=request.user
            )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


from django.shortcuts import get_object_or_404


class ContactDetailView(APIView):

    permission_classes = [HasActiveOrganization]

    def get_contact(self, request, contact_id):
        return get_object_or_404(
            Contact,
            id=contact_id,
            organization=request.organization
        )

    def get(self, request, contact_id):

        contact = self.get_contact(request, contact_id)

        serializer = ContactSerializer(contact)

        return Response(serializer.data)

    def put(self, request, contact_id):

        contact = self.get_contact(request, contact_id)

        serializer = ContactSerializer(
            contact,
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, contact_id):

        contact = self.get_contact(request, contact_id)

        serializer = ContactSerializer(
            contact,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, contact_id):

        contact = self.get_contact(request, contact_id)

        contact.delete()

        return Response(
            {"message": "Contact deleted successfully."},
            status=status.HTTP_200_OK
        )