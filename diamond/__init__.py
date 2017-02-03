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

# The import statements below allow exporting symbols, hence the NOQA markers.

import diamond.cli      # NOQA
import diamond.filters  # NOQA
import diamond.i18n     # NOQA
import diamond.auth     # NOQA
import diamond.tasks    # NOQA
import diamond.routes   # NOQA
import diamond.admin    # NOQA
import diamond.user     # NOQA
import diamond.errors   # NOQA

from diamond.app import app

__version__ = '0.4.1'
__all__ = ['app', 'main']


def main():
    app.run(host=app.config['HOST'], port=app.config['PORT'])
