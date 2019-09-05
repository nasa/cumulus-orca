DR Database
================

**DR** uses a [PostgreSQL](http://www.postgresql.org/) database as a backend to
manage and store the information related to the disaster recovery jobs. The
_**Installation**_ section below details the steps for installing the database objects
in a PostgreSQL cluster.


Installation
------------

Instalation of the DR application is straight forward and fairly automated. In all cases the
SQL commands should be run as the PostgreSQL super user. The super user is needed because the script
will create the database, users, roles, schemas and objects necessary for the application.

Prior to installing, verify the existance of the **disaster_recovery** database by logging into the PostgreSQL database
with the psql utility and run the *\l* command to see if the **disaster_recovery** database exists as seen below.

```bash
$>  psql -h elpdvx143.cr.usgs.gov --no-psqlrc postgres postgres

psql> \l
                                    List of databases
┌────────────────┬──────────┬──────────┬────────────┬────────────┬───────────────────────┐
│      Name      │  Owner   │ Encoding │  Collate   │   Ctype    │   Access privileges   │
├────────────────┼──────────┼──────────┼────────────┼────────────┼───────────────────────┤
│disaster        | postgres | UTF8     | en_US.UTF8 | en_US.UTF8 | =Tc/postgres          |
│     _recovery  |          |          |            |            | postgres=CTc/postgres |
│                |          |          |            |            | dr_role=c/postgres    |
│                |          |          |            |            | dbo=c/postgres        |
│postgres        | postgres | UTF8     | en_US.utf8 | en_US.utf8 |                       |
│template0       | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres           |
│                |          |          |            |            | postgres=CTc/postgres |
│template1       | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres           |
│                |          |          |            |            | postgres=CTc/postgres |
└────────────────┴──────────┴──────────┴────────────┴────────────┴───────────────────────┘

``` 

The output should be similar to above. Follow the proper instructions based on the existance or lack
thereof of the **disaster_recovery** database.

Use the following steps to install the the **DR** application into a PostgreSQL database cluster.

1.  Download the git repository:

    ```bash
    $> git clone https://git.earthdata.nasa.gov/scm/pocumulus/dr-podaac-swot.git
    ```
2. Move to the database base directory under database/ddl:

    ```bash
    $> cd database/ddl/base
    ```
3. If the **disaster_recovery** database currently exists based on the prior database *\\l* command, modify the init.sql
   file using a simple sed command seen below. The command will comment out the create syntax for the database.
   Otherwise skip this step and move on to step 4.

    ```bash
    $> sed -i 's/^\\ir database/-- \\ir database/' init.sql
    ```
4. Using the psql command line client install the database. The command below shows the basic syntax:

    ```bash
    $> psql --no-psqlrc --file=init.sql -U postgres postgres
    ```
5. Update the passwords for the dbo user and druser if needed. **Note**: *Password resets are only needed
for a user if a notice is seen informing the installer of the user creation (NOTICE: USER CREATED dbo!)*.
To update the passwords for a user log in as the postgres user via the psql client and run the
following commands replacing dbo for the proper username. Note that the passwords are shown below for
clarity, the command does not echo out the typed password characters in practice.:

    ```bash
    $> psql --no-psqlrc -U postgres postgres
    
    postgres=> \password dbo
    Enter new password: This_is_my_12_digit_pass
    Enter it again: This_is_my_12_digit_pass
    postgres=> commit;
    ```

If a pooling application like [PgBouncer](https://pgbouncer.github.io/) is used to pool connections in
front of the database, do not forget to configure connections to the newly created **disaster_recovery** database.
In addition do not forget to add any administrative extensions or other maintenance code commonly used
by the system administration staff.

The application user, schema and objects are now installed. Configure the database user credentials in
cloakware for the application.


Documentation
--------------

Full documentation on the schema, objects and relationships can be found under the doc folder. The *DR.zip* file
contains an HTML report of the schema. The *DR.xed* file can be used with Aqua Data Studio to explore the schema.
In addition, all code used to create the various users, roles, schema and objects are located under the *ddl/base
folder. The objects are organized under their respective folders. The init.sql details the order they are run and
the user they are run as. 
