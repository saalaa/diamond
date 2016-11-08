#!/bin/sh

# Allows using a `.env` file that exports environment variables; for example:
#
#   export FLASK_DEBUG=yes
#   export SECRET_KEY=xxx
if [ -e .env ]; then
  echo ' * Reading .env'
  cat .env | sed 's/^/   | /'

  source .env
fi

export FLASK_APP=diamond/__init__.py

flask $@
