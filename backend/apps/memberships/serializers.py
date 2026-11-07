from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class InvitationAcceptSerializer(serializers.Serializer):
    token = serializers.CharField()

    email = serializers.EmailField()

    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)

    password = serializers.CharField(
        write_only=True,
        min_length=12
    )

    password_confirm = serializers.CharField(
        write_only=True
    )

    def validate_email(self, value):
        return value.strip().lower()

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({
                "password_confirm": "Passwords do not match."
            })

        validate_password(attrs["password"])

        return attrs



from rest_framework import serializers
from apps.memberships.models import Membership


class EmployeeInvitationCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()

    role = serializers.ChoiceField(
        choices=[
            Membership.Role.ADMIN,
            Membership.Role.MANAGER,
            Membership.Role.EMPLOYEE,
        ]
    )

    def validate_email(self, value):
        return value.strip().lower()

class OrganizationSelectionSerializer(serializers.Serializer):
    organization_id = serializers.UUIDField()