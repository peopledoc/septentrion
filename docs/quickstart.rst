Quickstart
==========

Welcome to the *Septentrion* quickstart documentation.

In this tutorial, you will learn how to write migrations in the expected format, how to
visualize them and how to run them against a PostgreSQL database.

Prepare your database
---------------------

If you already have a PostgreSQL database around, make sure to note the connection
parameters. Otherwise, we'll create one together with Docker_:

.. _Docker: https://docs.docker.com/

.. code-block:: console

    $ docker run --detach --rm -p 5432:5432 --name septentrion_db postgres

.. note::

    If you need to stop the docker at some point, use ``docker stop septentrion_db``.

.. note::

    If you stop the Docker or reboot your machine, the Postgres database will be trashed and you will need to re-create
    one and add some data again.


You'll also need ``psycopg2``, which is notoriously complex to install. Septentrion
will install the ``psycopg2`` python package, but will expect the system to already
have the prerequisites (on ``Ubuntu``)::

    $ sudo apt install libpq-dev python-dev postgresql-client

.. note::
    On a different OS, if you experiment difficulties, we'll be grateful if you can tell
    us via an issue so that we improve this documentation.

Install and configure Septentrion
---------------------------------

Within a virtualenv_, install Septentrion with:

.. _virtualenv: https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments

.. code-block:: console

    (venv) $ pip install septentrion[psycopg2_binary]

Next we will configure the connection to the PostgreSQL database. We can do this either
with command line flags, environment variables or a configuration file. In this
tutorial, we will use a configuration file, ``septentrion.ini``.

.. code-block:: ini

    [septentrion]
    migrations_root=migrations
    host=localhost
    username=postgres
    # port=5432

.. note::

    With the Docker setup described above, you should be good to go.
    If you need additional configuration parameters to connect to your database, have a look at
    :ref:`advanced configuration options <configure>`.


Write migrations
----------------

Migrations are SQL files that are executed in order. Migrations are grouped together in
successive versions. All migrations in the same version are placed in a folder named
after the version number.

Let's create our migration folder, and a first version folder.

.. code-block:: console

    $ mkdir migrations
    $ mkdir migrations/1.0

Now we can add a migration file in ``migrations/1.0/`` named ``00-author.ddl.sql``:

.. code-block:: sql

    BEGIN;
    CREATE TABLE "author" (
        "id" serial NOT NULL PRIMARY KEY,
        "name" varchar(100) NOT NULL,
        "birth_date" varchar(10) NOT NULL
    );
    COMMIT;

.. note::

    Migrations are executed in alphabetical order, so an easy way to control the order is to prefix filenames with two
    digits.

.. note::

    ``ddl`` stands for *Data Definition Language* and corresponds to all the operations that change the structure of the
    database (``CREATE``, ``DROP``, ...).

Congratulations, you have now written your first *Septentrion* migration. Let's see how
to run it!


Run migrations
--------------

First, we want to visualize what is going to happen, without making any change to our
data yet.

.. code-block:: console

    $ septentrion --target-version 1.0 show-migrations

    Current version is None
    Target version is 1.0
    Version 1.0
      [ ] 00-author.ddl.sql



Great, we can now run it for real:

.. code-block:: console

    $ septentrion --target-version 1.0 migrate

    Applying migrations
    Version 1.0



.. note::

    You should run *septentrion* in your root directory, where your ``migrations`` folder is.

.. note::

    The ``--target-version`` flag is a required option (it might change in the future).


If something is not working as it should be, you probably want to check the
:ref:`troubleshooting guide <troubleshoot>`
or the :ref:`advanced options <advanced-options>`.

At this point, the ``author`` table has been created in the database. We can check that
and simulate our application by creating a few rows in the table.


.. code-block:: console

    $ psql --host localhost --user postgres postgres

    postgres=# \d

                          List of relations
     Schema |             Name              |   Type   |  Owner
    --------+-------------------------------+----------+----------
     public | author                        | table    | postgres
     public | author_id_seq                 | sequence | postgres
     public | septentrion_migrations        | table    | postgres
     public | septentrion_migrations_id_seq | sequence | postgres
     public | sql_version                   | table    | postgres
    (5 rows)

    postgres=# INSERT INTO author (name, birth_date)
    VALUES
    ('Victor Hugo', '1802-02-26'),
    ('George Gordon Byron', '1788-01-22'),
    ('JRR Tolkien', '1892-01-03');
    INSERT 0 3

    postgres=# SELECT * FROM author;
     id |        name         | birth_date
    ----+---------------------+---------------
      0 | Victor Hugo         | 1802-02-26
      1 | George Gordon Byron | 1788-01-22
      2 | JRR Tolkien         | 1892-01-03
    (3 rows)



A more complex migration
------------------------

For version ``2.0`` of our application, we want to change ``birth_date`` from
``varchar`` to the ``date`` type.

We create a new folder for the version.

.. code-block:: console

    $ mkdir migrations/2.0

We can add the migration file in ``migrations/2.0/`` named
``00-change_birth_date_type.ddl.sql``:

.. code-block:: sql

    BEGIN;
    ALTER TABLE author
        ALTER COLUMN birth_date
        TYPE DATE USING to_date(birth_date, 'YYYY-MM-DD');
    COMMIT;


We launch the migration.

.. code-block:: console

    $ septentrion --target-version 2.0 migrate

    Applying migrations
    Version 1.0
      [X] Already applied
    Version 2.0
      [X] Applied 00-change_birth_date_type.ddl.sql

Now we can check that our migration successfully changed the column type in the
``author`` table.

.. code-block:: console

    $ psql --host localhost --user postgres postgres
    postgres=# SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'author';
      column_name  |     data_type
    ---------------+-------------------
     id            | integer
     name          | character varying
     date_of_birth | date
    (3 rows)



Congratulations, you can now run migrations with *Septentrion*!

Going further
-------------

To continue with practical steps, head to the :ref:`How-to... <how-to>` section.

If you want to better understand some design decisions, head to the :ref:`Discussions
<discussions>` sections.


.. toctree::
   :maxdepth: 2

   howto_index
   discussions
