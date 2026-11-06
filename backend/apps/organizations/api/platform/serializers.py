from rest_framework import serializers


class OrganizationCreateSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=150)

    slug = serializers.SlugField(max_length=180)

    description = serializers.CharField(
        required=False,
        allow_blank=True
    )

    owner_email = serializers.EmailField()

    def validate_name(self, value):
        return value.strip()

    def validate_owner_email(self, value):
        return value.strip().lower()