Septentrion: A CLI tool to apply PostgreSQL migrations to a database
====================================================================

.. image:: https://badge.fury.io/py/septentrion.svg
    :target: https://pypi.org/pypi/septentrion
    :alt: Deployed to PyPI

.. image:: https://readthedocs.org/projects/septentrion/badge/?version=latest
    :target: http://septentrion.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/github/workflow/status/peopledoc/septentrion/CI?logo=github
    :target: https://github.com/peopledoc/septentrion/actions?workflow=CI
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
migrations, because you prefer your migrations to be manually written in SQL. Then your
tool would be django-north_.

But maybe you're not using Django. You would like a standalone migration tool. You're
looking for Septentrion. Congratulations, you've found it.

Septentrion supports PostgreSQL 9.6+ & Python 3.6+, and requires the ``psql``
executable to be present on the system.

.. _South: https://bitbucket.org/andrewgodwin/south/src
.. _django-north: https://github.com/peopledoc/django-north

Very quick start
----------------

- *Step 0*: Install with ``pip install septentrion[psycopg2_binary]`` (or
  ``pip install septentrion[psycopg2]`` if you know what you're doing)

- *Step 1*: Create a folder for the version, and add some migration files.

.. code-block:: console

    migrations/
    └──  1.0
        ├── 1.0-0-version-dml.sql
        ├── 1.0-author-1-ddl.sql
        └── 1.0-author-2-dml.sql

- *Step 2*: Run septentrion

.. code-block:: console

    $ septentrion --target-version 1.0 migrate

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
