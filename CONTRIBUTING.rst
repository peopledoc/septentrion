Contributing
============

Let's head north, welcome to Septentrion!

This contributing guide is trying to avoid common pitfalls, but the project
development environment is quite common. If it's not your first rodeo, here's a TL;DR:

.. code-block:: console

    $ sudo apt install postgresql-client
    $ docker-compose up -d
    $ export PGDATABASE=septentrion PGHOST=localhost PGUSER=postgres PGPASSWORD=password
    $ createdb
    $ scripts/bootstrap
    $ scripts/tests
    $ scripts/lint
    $ scripts/docs

This project uses Poetry_, pre-commit_. We recommand installing those with
pipx_. You will need a ``PostgreSQL`` database, which you can either setup from
`docker-compose`_ or set up on your own (e.g. with ``pg_virtualenv``).

.. _Poetry: https://python-poetry.org/
.. _pre-commit: https://pre-commit.com
.. _pipx: https://pipxproject.github.io/pipx/installation/
.. _`docker-compose`: https://docs.docker.com/compose

There are multiple ways of interacting with the project.


I want to setup a database for contributing & running tests
-----------------------------------------------------------

The development database can be launched using docker with a single command.
The PostgreSQL database we used is a fresh standard out-of-the-box database
on the latest stable version.

.. code-block:: console

    $ sudo apt install postgresql-client  # debian
    $ docker-compose up -d
    $ export PGDATABASE=septentrion PGHOST=localhost PGUSER=postgres PGPASSWORD=password
    $ createdb

I want to prepare my development environment
--------------------------------------------

The ``bootstrap`` script will install ``poetry`` and ``pre-commit`` through ``pipx``
for you. If ``pipx`` is not installed, it will be added too.

.. code-block:: console

    $ scripts/bootstrap

I just want to run the CI checks locally
----------------------------------------

.. code-block:: console

    $ scripts/tests
    $ scripts/lint
    $ scripts/docs

Please inspect those scripts, you'll see that they are very short. You're free to
use the command they describe directly, there's nothing wrong in that.

I want a venv to play locally
-----------------------------

Use poetry. Look at ``poetry env use python3.X`` if you want to work on a specific
Python version.

I want a quicker feedback loop
------------------------------

Running ``poetry run`` takes a good second or more. If you want to speed up thing,
create a shell in your virtual environment:

.. code-block:: console

    $ poetry shell

From here, you can launch commands directly, such as ``pytest``

I want to build the documentation
---------------------------------

Build with:

.. code-block:: console

    $ scripts/docs
    $ python -m webbrowser docs/_build/html/index.html

Run spell checking on the documentation (optional):

.. code-block:: console

    $ sudo apt install enchant
    $ scripts/docs-spelling

Because of outdated software and version incompatibilities, spell checking is not
checked in the CI, and we don't require people to run it in their PR. Though, it's
always a nice thing to do. Feel free to include any spell fix in your PR, even if it's
not related to your PR (but please put it in a dedicated commit).

If you need to add words to the spell checking dictionary, it's in
``docs/spelling_wordlist.txt``. Make sure the file is alphabetically sorted.

If Sphinx's console output is localized and you would rather have it in English,
use the environment variable ``LC_ALL=C.utf-8`` (either exported or attached to the
``tox`` process)

I want to hack around
---------------------

You're invited to hack around! We have set up those tools to ease usual developpement
but we're always doing our best so that you can remove the top layers and work
the way you prefer. For example: you can use ``pytest`` or ``black`` as-is, without
all the tools. It's even recommanded to remove layers when things become complicated.

The base commands are in the ``scripts/`` folder.

I want a working setup to iterate from
--------------------------------------

With a running database:

.. code-block:: console

    (venv) $ export SEPTENTRION_MIGRATIONS_ROOT=example_migrations
    (venv) $ septentrion migrate

Core contributor additional documentation
-----------------------------------------

Release a new version
^^^^^^^^^^^^^^^^^^^^^

There should be an active Release Draft with the changelog in GitHub releases. Make
relevant edits to the changelog. Click on Release, that's it, the rest is automated.

When creating the release, GitHub will save the release info and create a tag with the
provided version. The new tag will be seen by GitHub Actions, which will then create a
wheel (using the tag as version number, thanks to our ``setup.py``), and push it to PyPI
(using the new API tokens). That tag should also trigger a ReadTheDocs build, which will
read GitHub releases which will write the changelog in the published documentation.

.. note::

    If you need to edit the name or body of a release in the GitHub UI, don't forget to
    also rebuild the stable and latest doc on readthedocs__.

.. __: https://readthedocs.org/projects/septentrion/
