File naming convention
----------------------

We recommend to use the following naming convention for migration files:

.. code-block:: console

    [VERSION]-[MIGRATION]-[ORDER]-[TYPE].sql

 - version : the release version

 - migration : a free name for the migration

 - order : a number used to order the files inside the migration

 - type : ddl or dml, ddl if the file contains schema migration, dml if the file contains data migration.