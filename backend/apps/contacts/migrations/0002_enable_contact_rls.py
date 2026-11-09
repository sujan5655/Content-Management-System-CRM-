
from django.db import migrations


ENABLE_RLS = """
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;

ALTER TABLE contacts FORCE ROW LEVEL SECURITY;

CREATE POLICY contacts_tenant_isolation
ON contacts
FOR ALL
TO crm_app
USING (
    organization_id =
    NULLIF(
        current_setting('app.current_organization_id', true),
        ''
    )::uuid
)
WITH CHECK (
    organization_id =
    NULLIF(
        current_setting('app.current_organization_id', true),
        ''
    )::uuid
);
"""


DISABLE_RLS = """
DROP POLICY IF EXISTS contacts_tenant_isolation ON contacts;

ALTER TABLE contacts NO FORCE ROW LEVEL SECURITY;

ALTER TABLE contacts DISABLE ROW LEVEL SECURITY;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("contacts", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql=ENABLE_RLS,
            reverse_sql=DISABLE_RLS
        ),
    ]
