[![Build status](https://travis-ci.org/saalaa/diamond.svg?branch=master)](https://travis-ci.org/saalaa/diamond)

# Diamond Wiki

The metadata enabled wiki engine.


## Running on Heroku

The simplest is probably to use the following button:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/saalaa/diamond)

But if you want to do it manually and/or intend to make meaningful changes to
Diamond Wiki, we've got you covered. First, you should download and install the
[Heroku CLI](https://devcenter.heroku.com/articles/heroku-command-line).

Then, create a new Heroku app:

    $ heroku create

Add a PostgreSQL resource to the Heroku app (it doesn't have to be the free
plan, please refer to Heroku documentation for alternative plans):

    $ heroku addons:create heroku-postgresql:hobby-dev

You can now deploy the application to Heroku:

    $ git push heroku

Finally it's time to initialize the database and load fixtures:

    $ heroku run scripts/bootstrap.sh

The following chapters should also provide plenty of information on how to
further configure the installation.


## Running Elsewhere

We will only cover using `virtualenv` for simplicity, so let's start with
creating a new environment and activating it:

    $ virtualenv env
    $ source env/bin/activate

Now, let's install dependencies:

    $ pip install -r requirements.txt

It's now time to initialize the database and load fixtures (this is strictly
equivalent to running `scripts/bootstrap.sh`):

    $ scripts/diamond.sh db upgrade
    $ scripts/diamond.sh load-fixtures

Finally, we can run the wiki:

    $ scripts/diamond.sh run


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
