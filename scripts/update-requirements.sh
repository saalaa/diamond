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

if [ "$1" = "" ]; then
  echo "Usage: $0 REQUIREMENTS"
  exit 1
fi

NEW_REQUIREMENTS=`pip list --outdated --format legacy | \
  awk '{ print $1 "==" $5; }'`

for line in $NEW_REQUIREMENTS; do
  library=`echo $line | awk -F= '{ print $1; }'`

  echo $library

  # Some `sed` implementations don't support `-i` properly.
  sed "s/^$library==.*/$line/" $1 > \
    /tmp/$1.$$

  mv /tmp/$1.$$ $1
done
