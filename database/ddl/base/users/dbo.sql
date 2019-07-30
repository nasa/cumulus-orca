DO LANGUAGE plpgsql
$$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_user where usename='dbo') THEN
        -- Create dbo
        CREATE ROLE dbo
            LOGIN
            INHERIT;

        -- Add Comment
        COMMENT ON ROLE dbo 
            IS 'GROUP: owner, DESCRIPTION: Non privelaged user who owns all application objects.';

        -- Set Default Session settings
        ALTER ROLE dbo SET maintenance_work_mem = '1GB';
        ALTER ROLE dbo SET work_mem = '1GB';
        ALTER ROLE dbo SET temp_buffers = '1GB';
        ALTER ROLE dbo SET temp_file_limit = -1;

        RAISE NOTICE 'USER CREATED dbo. PLEASE UPDATE THE USERS PASSWORD!';

    ELSE
        RAISE NOTICE 'dbo USER ALREADY EXISTS.';

    END IF;

    -- Grants
    GRANT CONNECT ON DATABASE labsndbx TO dbo;
END
$$;
