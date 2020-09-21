.. _configure:

Configure
=========

Configure database connection settings
--------------------------------------

# TODO expand documentation on database connection

Ensure that your database connection settings are correctly configured.

 - Either your environment variables `PGHOST`, `PGPORT` and `PGUSER` are properly set.
 - Or you can set the environment variables `SEPTENTRION_HOST`, `SEPTENTRION_PORT`, `SEPTENTRION_USERNAME`.
 - configuration file `septentrion.ini`
 - If you don't want to use environment variables, you can use the `--host`, `--port` or `--username` options
   when running the migration.


Configure extra files settings
------------------------------

If you need additional schema files to initialize your database
you can use specify to list of files, one for the files that must be run before the main schema,
and one for the files that must be run after.

In your configuration file you can add:

.. code-block:: ini

    [septentrion]
    ...
    before_schema_file=
        extra_file.sql
        another_file.sql
    after_schema_file=
        after_schema_file.sql

You can also use the cli options `--before-schema-file` and `--after-schema-file`.