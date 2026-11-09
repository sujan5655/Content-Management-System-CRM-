from rest_framework import serializers
from apps.contacts.models import Contact


class ContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contact

        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "company",
            "job_title",
            "notes",
            "created_by",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_by",
            "created_at",
            "updated_at",
        ]