Septentrion: A CLI tool to apply PostgreSQL migrations to a database
====================================================================

.. image:: https://badge.fury.io/py/septentrion.svg
    :target: https://pypi.org/pypi/septentrion
    :alt: Deployed to PyPI

.. image:: https://readthedocs.org/projects/septentrion/badge/?version=latest
    :target: http://septentrion.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://travis-ci.org/peopledoc/septentrion.svg?branch=master
    :target: https://travis-ci.org/peopledoc/septentrion
    :alt: Continuous Integration Status

.. image:: https://codecov.io/gh/peopledoc/septentrion/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/peopledoc/septentrion
    :alt: Coverage Status

.. image:: https://img.shields.io/badge/License-MIT-green.svg
    :target: https://github.com/peopledoc/septentrion/blob/master/LICENSE
    :alt: MIT License

.. image:: https://img.shields.io/badge/Contributor%20Covenant-v1.4%20adopted-ff69b4.svg
    :target: CODE_OF_CONDUCT.md
    :alt: Contributor Covenant

Overview
--------

Maybe you're looking for a tool to take care of Database migrations in your project. For
Django projects, that tool used to be South_ and then it became Django
itself.

But maybe you're looking for a tool that just focuses on running existing SQL migrations
and keeping track of what was applied. Your tool of choice would not generate those
migration, because you prefer your migrations to be manually written in SQL. Then your
tool would be django-north_.

But maybe you're not using Django. You would like a standalone migration tool. You're
looking for septentrion. Congratulations, you've found it.

Septentrion supports PostgreSQL 9.6+ and Python 3.6+.

.. _South: https://bitbucket.org/andrewgodwin/south/src
.. _django-north: https://github.com/peopledoc/django-north

Very quick start
----------------

- *Step 1*: Write your PostgreSQL migrations, name files and folders according to
  a convention.
  See the folder `example_migrations` for an example:

.. code-block:: console

    example_migrations/
    ├── 0.1
    ├── 1.0
    │   ├── 1.0-0-version-dml.sql
    │   ├── 1.0-author-1-ddl.sql
    │   ├── 1.0-author-2-dml.sql
    │   ├── 1.0-book-1-ddl.sql
    │   └── 1.0-book-2-dml.sql
    ├── 1.1
    │   ├── 1.1-0-version-dml.sql
    │   ├── 1.1-add-num-pages-1-ddl.sql
    │   ├── 1.1-add-num-pages-2-dml.sql
    │   └── 1.1-index-ddl.sql
    ├── 1.2
    │   ├── 1.2-0-version-dml.sql
    │   ├── 1.2-remove-author-dob-ddl.sql
    │   └── 1.2-rename-num-pages-ddl.sql
    ├── 1.3
    │   ├── 1.3-0-version-dml.sql
    │   ├── 1.3-add-readers-ddl.sql
    │   ├── 1.3-add-readers-dml.sql
    │   ├── 1.3-remove-author-dob-ddl.sql
    │   └── 1.3-rename-num-pages-ddl.sql
    ├── fixtures
    │   ├── fixtures_0.1.sql
    │   └── fixtures_1.0.sql
    └── schemas
        └── schema_0.1.sql

- *Step 2*:

.. code-block:: console

    $ septentrion --target-version 1.2 migrate

- *Step 3*: That's it.

.. Below this line is content specific to the README that will not appear in the doc.
.. end-of-index-doc

We're currently working on this tool, and it's been used internally since 2018, but
for now, if you want to use it without a direct access to the people who
wrote it, you're going to have a lot of questions. We expect a proper documentation
to be ready by mid-2020. Please feel free to contact us meanwhile.

Where to go from here
---------------------

The complete docs_ is probably the best place to learn about the project.

You can check the quickstart_ guide to start running your first migrations.

If you encounter a bug, or want to get in touch, you're always welcome to open a
ticket_.

.. _docs: http://septentrion.readthedocs.io/en/latest
.. _quickstart: http://septentrion.readthedocs.io/en/latest/quickstart.html
.. _ticket: https://github.com/peopledoc/septentrion/issues/new
