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

Overview
--------

- *Step 1*: Write your PostgreSQL migrations, name files and folders according to
  a convention.
- *Step 2*:

.. code-block:: console

    $ septentrion migrate

- *Step 3*: That's it.

.. Below this line is content specific to the README that will not appear in the doc.
.. end-of-index-doc

Where to go from here
---------------------

The complete docs_ is probably the best place to learn about the project.

If you encounter a bug, or want to get in touch, you're always welcome to open a
ticket_.

.. _docs: http://septentrion.readthedocs.io/en/latest
.. _ticket: https://github.com/peopledoc/septentrion/issues/new