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

from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required
from flask_babel import gettext as _
from diamond import mail
from diamond.db import db
from diamond.app import app
from diamond.auth import current_user
from diamond.models import User, Document, Token
from diamond.utils import serialize_request


@app.route('/user/dashboard')
@login_required
def user_dashboard():
    contributions = Document.query \
            .filter(Document.user_id == current_user.id) \
            .count()

    if not current_user.validated:
        flash(_('You have not yet confirmed your email address. Send a '
          '<a href="/user/send-confirmation">confirmation link</a>?'))

    return render_template('user-dashboard.j2', contributions=contributions)


@app.route('/user/account', methods=['GET', 'POST'])
@login_required
def user_account():
    def respond(message=None):
        if message:
            flash(message)

        return render_template('user-account.j2')

    if not current_user.validated:
        flash(_('You have not yet confirmed your email address. Send a '
          '<a href="/user/send-confirmation">confirmation link</a>?'))

    if request.method == 'GET':
        return respond()

    if request.form.get('action') == 'change-name':
        name = request.form.get('name')
        current_user.name = name
        current_user.save()

        db.session.commit()

    if request.form.get('action') == 'change-email':
        email = request.form.get('email')
        password = request.form.get('password')

        if User.exists(email=email):
            return respond(_('This email address is already in use'))

        if User.exists(name=name):
            return respond(_('This name is already in use'))

        if not current_user.check_password(password):
            return respond(_('The password you entered did not match your '
                'current password'))

        current_user.email = email
        current_user.validated = False
        current_user.save()

        token = Token.make(current_user, email)
        token.save()

        db.session.commit()

        mail.send_confirmation.delay(email, token.digest)

    if request.form.get('action') == 'change-password':
        current_password = request.form.get('current-password')
        new_password = request.form.get('new-password')

        if not current_user.check_password(current_password):
            return respond(_('The password you entered did not match your '
                'current password'))

        current_user.set_password(new_password)
        current_user.save()

        db.session.commit()

    return respond()


@app.route('/user/send-confirmation')
@login_required
def send_confirmation():
    token = Token.make(current_user, current_user.email)
    token.save()

    db.session.commit()

    context = serialize_request(request)
    mail.send_confirmation.delay(context, current_user.email, token.digest)

    return redirect(url_for('user_dashboard'))
