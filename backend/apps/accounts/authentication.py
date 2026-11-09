from django.db import connection

from rest_framework_simplejwt.authentication import JWTAuthentication


class TenantJWTAuthentication(JWTAuthentication):

    def authenticate(self, request):
        result = super().authenticate(request)

        if result is None:
            return None

        user, validated_token = result

        organization_id = validated_token.get("organization_id", "")

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    set_config('app.current_user_id', %s, true),
                    set_config('app.current_organization_id', %s, true)
                """,
                [
                    str(user.id),
                    str(organization_id or "")
                ]
            )

        return user, validated_token