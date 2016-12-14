#!/bin/sh

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

ROOT=http://diamond-wiki.herokuapp.com

FIXTURES="
  activate-help.md
  deactivate-help.md
  diff-help.md
  edit-help.md
  front-page.md
  history-help.md
  main-menu.md
  metadata.md
  recent-changes-help.md
  sandbox.md
  search-help.md
  settings-help.md
  sign-in-help.md
  sign-up-help.md
  title-index-help.md
"

rm fixtures/*.md

for fixture in $FIXTURES; do
  echo $ROOT/$fixture
  curl -so fixtures/$fixture $ROOT/$fixture
done
