/*
** SCHEMA: dr
**
** USER: druser
**
*/

-- Create a user
DO LANGUAGE plpgsql
$$
BEGIN
        DROP ROLE IF EXISTS druser;
        IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = 'druser' ) THEN
        -- Create druser
        CREATE ROLE druser
            LOGIN
            INHERIT
            IN ROLE dr_role;

        -- Add comment
        COMMENT ON ROLE druser
            IS 'GROUP: application-dr, DESCRIPTION: dr application user.';

    END IF;

    -- Alter the roles search path so on login it has what it needs for a path
    ALTER ROLE druser SET search_path = dr, public;
END
$$;
