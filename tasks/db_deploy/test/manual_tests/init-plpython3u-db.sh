#!/bin/bash
set -e

# Install the plpython3u extension in the template database so that it will be
# available in the ORCA database when it is created. This is done to replicate
# the aws_s3 extension install based off of the forked one available on github at
# //github.com/chimpler/postgres-aws-s3.git
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname template1 <<-EOSQL
    CREATE EXTENSION plpython3u;
EOSQL
