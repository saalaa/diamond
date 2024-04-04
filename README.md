# Diamond Wiki

The metadata enabled wiki engine.

## Working on the Wiki Engine

### Envrionment Setup

Follow the official [install
instructions](https://asdf-vm.com/guide/getting-started.html) and then install
the necessary plugins:

    $ asdf plugin add poetry
    $ asdf plugin add pre-commit
    $ asdf plugin add python

Now install the required tooling:

    $ asdf install

Install Python requirements:

    $ poetry install

Prepare the database:

    $ poetry run flask -A diamond.app db upgrade
    $ poetry run flask -A diamond.app load-fixtures

Run the wiki engine:

    $ poetry run flask -A diamond.app run

### Testing

    $ poetry run pytest


## Configuration

Configuration is entirely done through environment variables (which means the
code base is friendly with most PaaS and orchestration solutions).

Here's a full list of supported environment variables:

- `SQL_DEBUG`: Enable output of SQL statements. Set to `yes` to enable. Should
  not be set on production.
- `FLASK_DEBUG`: Enable pretty exceptions and automatic code reloading while
  hacking Diamond Wiki. Set to `yes` to enable. Must not be set on production.
- `DATABASE_URL`: Database connection credentials. Defaults to
  `sqlite:///diamond.db`.
- `REDIS_URL`: Redis connection credentials. Defaults to `redis://mock` which
  doesn't require Redis to work.
- `SECRET_KEY`: Secret key for encrypting and signing things. Defaults to a
  random value.
- `MAIL_SERVER`: SMTP server address and port.
- `MAIL_USE_TLS`: Whether or not the SMTP server supports TLS.
- `MAIL_USE_SSL`: Whether or not the SMTP server supports SSL.
- `MAIL_USERNAME`: SMTP user name.
- `MAIL_PASSWORD`: SMTP password.
- `MAIL_DEFAULT_SENDER`: Default sender used for all communication with users,
  for example: `Diamond Wiki <diamond-wiki@example.com>`.

When running Diamond wiki through Gunicorn (on Heroku for example) or directly
through Python (`python -m diamond`), the following variables are taken into
account: `HOST`, `PORT`.

When using `scripts/diamond.sh run`, the host and port can be configured
through command-line options. Furthermore, `scripts/diamond.sh` supports an
`.env` file that is able to export environment variables, making development
easier (it then prints its content):

    $ scripts/diamond.sh run
     * Reading .env
       | export FLASK_DEBUG=
       | export SECRET_KEY=xxx
     * Serving Flask app "diamond"
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)


## Testing

Although full code base coverage is the goal, testing is a work in progress.

### Manual tests using `pytest`

The simplest way to run the tests is through calling `pytest` in which case
whatever environment you have setup is used. This is what developpers do more
often than not, reusing their development environment:

First, a virtual environment with the project's dependencies is needed:

    $ virtualenv env
    $ source env/bin/activate
    $ pip install -r requirements.txt

Then, `pytest` can be called:

    $ pytest

### Manual tests using `tox`

A more complex way to run the tests is through calling `tox` in which case
environment and dependencies are handled automatically. In `tox.ini` several
Python versions can be configured as test environments (currently Python 2.7
and 3.5 are supported).

Using this method still relies on `pytest` so these must be configured
properly. It also expects the project to be `setuptools` -ready so that must be
configured properly as well.

You'll need `tox` installed (in this case in a virtual environment to avoid
polluting your system):

    $ virtualenv env
    $ source env/bin/activate
    $ pip install tox

Then, `tox` can be called:

    $ tox
