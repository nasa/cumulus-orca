-- Create the dr Application dbo Group

-- Create the Application role  if it does not exist
DO LANGUAGE plpgsql
    $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_group WHERE groname = 'drdbo_role' ) THEN
            -- Create Application Role
            CREATE ROLE drdbo_role
                NOLOGIN
                INHERIT;

            -- Add role comment
            COMMENT ON ROLE drdbo_role
                IS 'GROUP: application-dr, Group that contains all the permissions necessary for the dr application owner.';

        END IF;
            -- Grants
        GRANT CONNECT ON DATABASE labsndbx TO drdbo_role;
        GRANT CREATE ON DATABASE labsndbx TO drdbo_role;
    END
    $$;

COMMIT;

