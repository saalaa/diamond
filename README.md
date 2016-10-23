# Diamond Wiki

Quick-quick implementation of WikiWikiWeb in Python.

This is the enhanced implementation of Diamond Wiki, the meta-data capable Wiki
engine.

It features an extended faceted navigation, Markdown syntax and multiple
databases support.

## Running the Wiki

### On Heroku

First, you should install and download the [Heroku
CLI](https://devcenter.heroku.com/articles/heroku-command-line).

Then, you should create a new app on Heroku's website. For simplicity, that
app's name will be `APP_NAME` below; replace it with whatever you chose.

You'll want to add a database resource to your Heroku app and add its
connection string to the environment variables passed to your app.

Then, it's time to clone the repository and configure the Heroku CLI for
deployment:

    $ git clone https://bitbucket.org/saalaa/diamond
    $ cd diamond

    $ heroku login
    $ heroku git:remote -a APP_NAME

    $ git push heroku

Visit http://APP_NAME.herokuapp.com/initdb.

After you've visited `/initdb`, you should add the following environment
variable:

    PREVENT_INITDB=yes
