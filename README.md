# Septentrion

[![Build Status](https://travis-ci.org/peopledoc/septentrion.svg?branch=master)](https://travis-ci.org/peopledoc/septentrion) [![codecov](https://codecov.io/gh/peopledoc/septentrion/branch/master/graph/badge.svg)](https://codecov.io/gh/peopledoc/septentrion)

> A CLI tool to apply PostgreSQL migrations to a database.

## Overview

You're looking for a tool to take care of Database migrations in your project. For Django projects, that tool used to be [`South`](https://bitbucket.org/andrewgodwin/south/src), and then it became Django itself.

But you're looking for a tool that just focuses on running existing SQL migrations and keeping track of what was applied, through time. That's [`django-north`](https://github.com/peopledoc/django-north).

You're looking for that, but without Django. You're looking for septentrion. Congratulations, you've found it.

## Requirements

This project would only work for PostgreSQL databases 9.6+. We aim to be compatible with Python 2.7+ and Python 3+ (but Python 2 will not stay for long).

## Install

At the moment, there are no proper releases on PyPI. As a consequence, you'll have to clone this repository locally and install it via:

```sh
pip install git+https://github.com/peopledoc/septentrion.git
```

## What does it do?

Project is still pre-alpha, moving fast and breaking things. Best way to know what it does, is to call:

```sh
septentrion --help
```

----

## Launch a postgres DB with Docker

```console
$ docker run --rm -it -p 5432:5432 -e POSTGRES_PASSWORD=password postgres
```

## Licensing

`septentrion` is published under the terms of the Apache Software License.


## Testing

Nothing is done so far, but we have some guidelines we'd like to follow,
[here](tests/README.md)

### Running the tests

You must have access to a postgres database, then:

```bash
PGPASSWORD=password PGHOST=127.0.0.1 PGUSER=postgres PGPORT=5432 tox
```
