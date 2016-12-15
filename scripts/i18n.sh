#!/bin/sh -e

# Copyright (C) 1999, 2000 Martin Pool <mbp@humbug.org.au>
# Copyright (C) 2003 Kimberley Burchett <http://www.kimbly.com>
# Copyright (C) 2016 Benoit Myard <myardbenoit@gmail.com>
#
# This file is part of Diamond wiki.
#
# Diamond wiki is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Diamond wiki is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Diamond wiki. If not, see <http://www.gnu.org/licenses/>.

SOURCE_DIR=diamond
I18N_DIR=$SOURCE_DIR/i18n

TEMPLATE=$I18N_DIR/messages.pot

CONFIG=babel.cfg

show_help ()
{
  if [ "x$1x" != "xx" ]; then
    echo "Error: $1"
  fi

  echo "Usage: $0 COMMAND [OPTIONS]"
  echo
  echo "Available commands:"
  echo
  echo "  extract"
  echo "    Extract translatable strings from code base, store them in a"
  echo "    translation template (not to be modified manually)."
  echo
  echo "  init LANGUAGE"
  echo "    Create a new language using the translation template."
  echo
  echo "  update"
  echo "    Update existing languages using the translation template."
  echo
  echo "  compile"
  echo "    Compile all existing language translations files for release."

  if [ "x$1x" = "xx" ]; then
    exit 0
  else
    exit 1
  fi
}

case "$1" in

  extract)
    pybabel extract -F $CONFIG -k lazy_gettext -o $TEMPLATE $SOURCE_DIR
    ;;

  init)
    if [ ! -f $TEMPLATE ]; then
      show_help "missing translation template, run extrat first."
    fi

    if [ "x$2x" = "xx" ]; then
      show_help "you must provide a language identifier."
    fi

    pybabel init -i $TEMPLATE -d $I18N_DIR -l $2
    ;;

  update)
    if [ ! -f $TEMPLATE ]; then
      show_help "missing translation template, run extrat first."
    fi

    pybabel update -i $TEMPLATE -d $I18N_DIR
    ;;

  compile)
    pybabel compile -d $I18N_DIR
    ;;

  -h|--help|help)
    show_help
    ;;

  *)
    show_help "unsupported command or option $1"
    ;;

esac
