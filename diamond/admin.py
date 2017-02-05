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

import json

from flask import request, render_template, redirect, url_for, flash, g
from flask_login import login_user, login_required
from flask_babel import gettext as _

from diamond.app import app
from diamond.db import db
from diamond.auth import current_user
from diamond.models import Parameter, param, User
from diamond.utils import get_int_arg


def handle_form(section):
    if not current_user.admin:
        error = _('You are not allowed to access this page')
        return render_template('error.j2', error=error), 403

    if request.method == 'GET':
        return render_template('admin-' + section + '.j2')

    params = request.form.get('params', '')
    for key in params.split():
        if not key:
            pass

        Parameter.set(key, request.form.get(key, ''))

    db.session.commit()

    Parameter.clear_cache()

    message = _('Your changes have been saved')
    flash(message)

    return redirect(url_for(section))


@app.route('/admin')
@login_required
def admin():
    return redirect(url_for('settings'))


@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def settings():
    return handle_form('settings')


@app.route('/admin/appearance', methods=['GET', 'POST'])
@login_required
def appearance():
    return handle_form('appearance')


@app.route('/admin/security', methods=['GET', 'POST'])
@login_required
def security():
    return handle_form('security')


@app.route('/admin/menu', methods=['GET', 'POST'])
@login_required
def menu():
    if not current_user.admin:
        error = _('You are not allowed to access this page')
        return render_template('error.j2', error=error), 403

    if request.method == 'GET':
        return render_template('admin-menu.j2')

    item = {
        'type': request.form.get('type', 'link'),
    }

    if item['type'] == 'link':
        item['title'] = request.form.get('title', 'Title')
        item['url'] = request.form.get('url', 'URL')

    menu = param('menu', g.DEFAULT_MENU, 'json') or {}
    menu.setdefault('items', []) \
        .append(item)

    Parameter.set('menu', json.dumps(menu))

    db.session.commit()

    Parameter.clear_cache()

    flash(_('Your changes have been saved'))

    return redirect(url_for('menu'))


@app.route('/admin/menu/remove/<int:i>')
@login_required
def menu_remove(i):
    menu = param('menu', g.DEFAULT_MENU, 'json') or {}
    menu.setdefault('items', [])

    menu['items'].pop(i)

    Parameter.set('menu', json.dumps(menu))

    db.session.commit()

    Parameter.clear_cache()

    flash(_('Your changes have been saved'))

    return redirect(url_for('menu'))


@app.route('/admin/menu/move-up/<int:i>')
@login_required
def menu_move_up(i):
    menu = param('menu', g.DEFAULT_MENU, 'json') or {}
    menu.setdefault('items', [])

    item = menu['items'].pop(i)

    i = len(menu['items']) if i == 0 else i - 1

    menu['items'].insert(i, item)

    Parameter.set('menu', json.dumps(menu))

    db.session.commit()

    Parameter.clear_cache()

    flash(_('Your changes have been saved'))

    return redirect(url_for('menu'))


@app.route('/admin/menu/move-down/<int:i>')
@login_required
def menu_move_down(i):
    menu = param('menu', g.DEFAULT_MENU, 'json') or {}
    menu.setdefault('items', [])

    item = menu['items'].pop(i)

    i = 0 if i >= len(menu['items']) else i + 1

    menu['items'].insert(i, item)

    Parameter.set('menu', json.dumps(menu))

    db.session.commit()

    Parameter.clear_cache()

    flash(_('Your changes have been saved'))

    return redirect(url_for('menu'))


@app.route('/admin/users')
@login_required
def users():
    if not current_user.admin:
        return render_template('error.j2', error=_('You are not allowed to '
            'access this page')), 403

    page_arg = get_int_arg('page', 1)

    users = User.get() \
            .paginate(page_arg, 100)

    if request.method == 'GET':
        return render_template('admin-users.j2', users=users)


@app.route('/admin/users/toggle-admin/<int:user>')
@login_required
def users_toggle_admin(user):
    if not current_user.admin:
        return render_template('error.j2', error=_('You are not allowed to '
            'access this page')), 403

    user = User.get(id=user)

    if not user == current_user:
        user.admin = not user.admin
        user.save()

        db.session.commit()

    return redirect(url_for('users'))


@app.route('/admin/users/impersonate/<int:user>')
@login_required
def users_impersonate(user):
    if not current_user.admin:
        return render_template('error.j2', error=_('You are not allowed to '
            'access this page')), 403

    user = User.get(id=user)

    login_user(user)

    return redirect(url_for('read'))
