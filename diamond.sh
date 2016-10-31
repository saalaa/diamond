#!/bin/sh

# Allows using a `.env` file that exports environment variables; for example:
#
#   export FLASK_DEBUG=yes
#   export SECRET_KEY=xxx
if [ -e .env ]; then
  source .env
fi

export FLASK_APP=diamond/__main__.py

flask $@
