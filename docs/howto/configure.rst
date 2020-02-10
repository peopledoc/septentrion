Configure database connection settings
--------------------------------------

# TODO expand documentation on database connection

Ensure that your database connection settings are correctly configured.

 - Either your environment variables `PGHOST`, `PGPORT` and `PGUSER` are properly set.
 - Or you can set the environment variables `SEPTENTRION_HOST`, `SEPTENTRION_PORT`, `SEPTENTRION_USERNAME`.
 - configuration file `septentrion.ini`
 - If you don't want to use environment variables, you can use the `--host`, `--port` or `--username` options
   when running the migration.