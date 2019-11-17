# Septentrion

[![Build Status](https://travis-ci.org/peopledoc/septentrion.svg?branch=master)](https://travis-ci.org/peopledoc/septentrion) [![codecov](https://codecov.io/gh/peopledoc/septentrion/branch/master/graph/badge.svg)](https://codecov.io/gh/peopledoc/septentrion)

A CLI tool to apply PostgreSQL migrations to a database.

## Overview

Maybe you're looking for a tool to take care of Database migrations in your project. For Django projects, that tool used to be [`South`](https://bitbucket.org/andrewgodwin/south/src), and then it became Django itself.

But maybe you're looking for a tool that just focuses on running existing SQL migrations and keeping track of what was applied. Your tool of choice would not generate those migration, because you prefer your migrations to be manually written in SQL. Then your tool is [`django-north`](https://github.com/peopledoc/django-north).

But you're not using Django. You would like a standalone migration tool. You're looking for septentrion. Congratulations, you've found it.

## Requirements

This project would only work for PostgreSQL databases 9.6+. We aim to be compatible with Python 3.6+.

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

## Launch a postgres DB with Docker compose

```console
$ docker-compose up -d
```

## Licensing

`septentrion` is published under the terms of the Apache Software License.


## Testing

Nothing is done so far, but we have some guidelines we'd like to follow,
[here](tests/README.md)

### Running the tests

You must have access to a postgres database, then:

```bash
PGHOST=127.0.0.1 PGUSER=postgres tox
```
