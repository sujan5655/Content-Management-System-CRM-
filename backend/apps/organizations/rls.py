def enable_tenant_rls(table_name, policy_name=None):
    """
    Generate SQL to enable tenant isolation for a table.
    """

    if not table_name.replace("_", "").isalnum():
        raise ValueError("Invalid table name")

    policy_name = policy_name or f"{table_name}_tenant_isolation"

    if not policy_name.replace("_", "").isalnum():
        raise ValueError("Invalid policy name")

    return f"""
        ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;
        ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY;

        CREATE POLICY {policy_name}
        ON {table_name}
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


def disable_tenant_rls(table_name, policy_name=None):
    """
    Generate SQL to remove tenant isolation from a table.
    """

    if not table_name.replace("_", "").isalnum():
        raise ValueError("Invalid table name")

    policy_name = policy_name or f"{table_name}_tenant_isolation"

    if not policy_name.replace("_", "").isalnum():
        raise ValueError("Invalid policy name")

    return f"""
        DROP POLICY IF EXISTS {policy_name} ON {table_name};
        ALTER TABLE {table_name} NO FORCE ROW LEVEL SECURITY;
        ALTER TABLE {table_name} DISABLE ROW LEVEL SECURITY;
    """