# West

> A CLI tool to apply PostgreSQL migrations to a database.

## Overview

You're looking for a tool to take care of Database migrations in your project. For Django projects, that tool used to be [`South`](https://bitbucket.org/andrewgodwin/south/src), and then it became Django itself.

But you're looking for a tool that just focuses on running existing SQL migrations and keeping track of what was applied, through time. That's [`django-north`](https://github.com/peopledoc/django-north).

You're looking for that, but without Django. You're looking for west. Congratulations, you've found it.

## Requirements

This project would only work for PostgreSQL databases 9.6+. We aim to be compatible with Python 2.7+ and Python 3+ (but Python 2 will not stay for long).

## Install

At the moment, there are no proper releases on PyPI. As a consequence, you'll have to clone this repository locally and install it via:

```sh
pip install git+https://github.com/peopledoc/west.git
```

## What does it do?

Project is still pre-alpha, moving fast and breaking things. Best way to know what it does, is to call:

```sh
west --help
```

----

## Licensing

`west` is published under the terms of the Apache Software License.
