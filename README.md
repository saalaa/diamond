# Diamond Wiki

The metadata enabled wiki engine.


## Running on Heroku

The simplest is probably to use the following button:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://bitbucket.com/saalaa/diamond)

But if you want to do it manually and/or intend to make meaningful changes to
Diamond Wiki, we've got you covered. First, you should download and install the
[Heroku CLI](https://devcenter.heroku.com/articles/heroku-command-line).

Then, create a new Heroku app:

    $ heroku create

Add a PostgreSQL resource to the Heroku app (it doesn't have to be the free
plan, please refer to Heroku documentation for alternative plans):

    $ heroku addons:create heroku-postgresql:hobby-dev

And finally deploy the repository to the Heroku app:

    $ git push heroku

The following chapters should also provide plenty of information on how to
further configure the installation.


## Running Elsewhere

We will only cover using `virtualenv` for simplicity, so let's start with
creating a new environment and activating it:

    $ virtualenv env
    $ source env/bin/activate

Now, let's install dependencies:

    $ pip install -r requirements.txt

Finally, we can run the wiki:

    $ sh diamond.sh run


## Configuration

Configuration is entirely done through environment variables (which means the
code base is friendly with most PaaS and orchestration solutions).

Here's a full list of supported environment variables:

- `SQL_DEBUG`: Enable output of SQL statements. Set to `yes` to enable. Should
  not be set on production.
- `FLASK_DEBUG`: Enable pretty exceptions and automatic code reloading while
  hacking Diamond Wiki. Set to `yes` to enable. Must not be set on production.
- `HOST`: Define the host the application listens on. Defaults to `0.0.0.0`.
- `PORT`: Define the port the application listens on. Defaults to `5000`.
- `DATABASE_URL`: Database connection credentials. Defaults to
  `sqlite:///diamond.db`.
- `SECRET_KEY`: Secret key for encrypting and signing things. Defaults to a
  random value.
- `FRONTPAGE`: Name of your installation's home page. Defaults to `front-page`.
- `COLORSCHEME`: Name of the colorscheme. Defaults to `purple` (blue, green,
  pink and purple available).
