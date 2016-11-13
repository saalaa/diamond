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

from diamond import app
from diamond.diff import unified_diff

def test_unified_diff():
    class run_unified_diff():
        def __init__(self, a, b, titles=False):
            self.a = a.replace(' ', '\n')
            self.b = b.replace(' ', '\n')
            self.titles = titles

        def __enter__(self):
            data = unified_diff(self.a, self.b, 'AAA', 'BBB') if self.titles \
                    else unified_diff(self.a, self.b)

            data = list(data)

            return '\n'.join(data)

        def __exit__(self, *args, **kwargs):
            pass

    with run_unified_diff('', '', True) as diff:
        assert 'AAA' in diff
        assert 'BBB' in diff

    with run_unified_diff('', '') as diff:
        assert 'AAA' not in diff
        assert 'BBB' not in diff

    with run_unified_diff('x', 'x') as diff:
        assert 'line-old' not in diff
        assert 'line-new' not in diff
        assert 'chunk-deleted' not in diff
        assert 'chunk-added' not in diff

    with run_unified_diff('x xax x', 'x xbx x') as diff:
        assert 'line-old' in diff
        assert 'line-new' in diff
        assert 'chunk-deleted' in diff
        assert 'chunk-added' in diff

        assert 'chunk-changed' not in diff

    with run_unified_diff('a', 'b') as diff:
        assert 'line-old' in diff
        assert 'line-new' in diff
        assert 'chunk-deleted' in diff
        assert 'chunk-added' in diff

        assert 'chunk-changed' not in diff

    with run_unified_diff('xxx', 'x xxx') as diff:
        assert 'line-old' not in diff
        assert 'line-new' in diff
        assert 'chunk-deleted' not in diff
        assert 'chunk-added' not in diff

        assert 'chunk-changed' not in diff

    with run_unified_diff('x xxx', 'xxx') as diff:
        assert 'line-old' in diff
        assert 'line-new' not in diff
        assert 'chunk-deleted' not in diff
        assert 'chunk-added' not in diff

        assert 'chunk-changed' not in diff
