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

from flask import request, render_template, redirect, url_for, flash

from slugify import slugify
from flask_login import LoginManager, login_user, logout_user, \
        AnonymousUserMixin

# The import statement below allows exporting symbol, hence the NOQA marker.

from flask_login import current_user # NOQA

from flask_babel import gettext as _
from diamond.app import app
from diamond.db import db
from diamond.models import User, Document
from diamond.maths import hash, generate

DEFAULT_COMMENT = 'Sign up'


class AnonymousUser(AnonymousUserMixin):
    admin = False


login_manager = LoginManager(app)
login_manager.anonymous_user = AnonymousUser
login_manager.login_view = 'sign-in'


@login_manager.user_loader
def user_loader(slug):
    return User.get(slug) if slug else None


@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    def respond(message=None):
        if message:
            flash(message)

        (result, question) = generate()
        checksum = hash(result)

        return render_template('sign-up.j2', menu=Document.get('main-menu'),
                help=Document.get('sign-up-help'), question=question,
                checksum=checksum)

    if request.method == 'GET':
        return respond()

    checksum = request.form['checksum']
    name = request.form['name']
    password = request.form['password']
    answer = request.form['answer']

    slug = slugify(name)

    if hash(answer) != checksum:
        message = _('You failed to answer the simple maths question')
        return respond(message)

    if User.exists(slug):
        message = _('This user name is unavailable')
        return respond(message)

    is_first = User.is_first()
    page = Document.get(slug)

    if not page.id:
        page.title = name
        page.author = slug
        page.comment = DEFAULT_COMMENT
        page.save()

    user = User(slug=slug, admin=is_first)
    user.set_password(password)

    user.save()

    db.session.commit()

    login_user(user)

    return redirect(url_for('read', slug=slug))


@app.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    def respond(message=None):
        if message:
            flash(message)

        return render_template('sign-in.j2', menu=Document.get('main-menu'),
                help=Document.get('sign-in-help'))

    if request.method == 'GET':
        return respond()

    name = request.form['name']
    password = request.form['password']

    slug = slugify(name)
    user = User.get(slug)

    if not user or not user.check_password(password):
        message = _('Wrong user name or password')
        return respond(message)

    login_user(user)

    return redirect(url_for('read', slug=user.slug))


@app.route('/sign-out')
def sign_out():
    logout_user()
    return redirect(url_for('read'))
