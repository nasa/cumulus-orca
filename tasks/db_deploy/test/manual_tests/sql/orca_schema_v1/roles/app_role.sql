/*
** SCHEMA: dr
**
** ROLE: dr_role
**
*/

-- Create the Application role  if it does not exist
DO LANGUAGE plpgsql
$$
BEGIN
        --DROP ROLE IF EXISTS dr_role;
        IF NOT EXISTS (SELECT 1 FROM pg_group WHERE groname = 'dr_role' ) THEN
        -- Create Application Role
        CREATE ROLE dr_role
            NOLOGIN
            INHERIT;

        -- Add role comment
        COMMENT ON ROLE dr_role
            IS 'GROUP: application-dr, Group that contains all the permissions necessary for the dr application.';

        -- Add Grants
        GRANT CONNECT ON DATABASE orca TO dr_role;

    END IF;
END
$$;
