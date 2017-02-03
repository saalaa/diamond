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

# The import statement below allows exporting symbol, hence the NOQA marker.

from flask_login import current_user # NOQA

from flask_babel import gettext as _
from flask import request, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, \
        login_required, AnonymousUserMixin

from diamond.app import app
from diamond.db import db
from diamond.models import User, Token
from diamond.maths import hash, generate


class AnonymousUser(AnonymousUserMixin):
    admin = False


login_manager = LoginManager(app)
login_manager.anonymous_user = AnonymousUser
login_manager.login_view = 'sign_in'


@login_manager.user_loader
def user_loader(user_id):
    return User.get(id=user_id) if user_id else None


@app.route('/auth/sign-up', methods=['GET', 'POST'])
def sign_up():
    def respond(message=None):
        if message:
            flash(message)

        (result, question) = generate()
        checksum = hash(result)

        return render_template('sign-up.j2', question=question,
                checksum=checksum)

    if request.method == 'GET':
        return respond()

    checksum = request.form['checksum']
    email = request.form['email']
    password = request.form['password']
    name = request.form['name']
    answer = request.form['answer']

    if hash(answer) != checksum:
        return respond(_('You failed to answer the simple maths question'))

    if User.exists(email=email):
        return respond(_('This email address is already in use'))

    if User.exists(name=name):
        return respond(_('This name is already in use'))

    is_first = User.is_first()

    user = User(email=email, name=name, admin=is_first)
    user.set_password(password)

    user.save()

    db.session.commit()

    token = Token.make(user, user.email)
    token.save()

    db.session.commit()

    login_user(user)

    user.sendmail('welcome', token=token.digest)

    return redirect(url_for('user_dashboard'))


@app.route('/auth/sign-in', methods=['GET', 'POST'])
def sign_in():
    def respond(message=None):
        if message:
            flash(message)

        return render_template('sign-in.j2')

    if request.method == 'GET':
        return respond()

    email = request.form['email']
    password = request.form['password']

    user = User.get(email)

    if not user or not user.check_password(password):
        return respond(_('Wrong user name or password'))

    login_user(user)

    if 'next' in request.args:
        return redirect(request.args.get('next'))

    return redirect(url_for('user_dashboard'))


@app.route('/auth/sign-out')
@login_required
def sign_out():
    logout_user()
    return redirect(url_for('read'))


@app.route('/auth/confirm/<token>')
@login_required
def confirm(token):
    token = Token.get(current_user, token)

    if not token.valid(current_user.email):
        return render_template('error.j2', error=_('The token supplied is '
            'invalid')), 403

    current_user.validated = True
    current_user.save()

    db.session.delete(token)
    db.session.commit()

    return redirect(url_for('user_dashboard'))
