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

from flask import request
from flask_mail import Mail, Message
from flask_babel import gettext as _

from diamond.app import app
from diamond.models import param


mail = Mail(app)


def send_welcome(recipient, token):
    service = param('title', 'Diamond wiki')

    scheme = request.scheme
    host = request.host

    subject = _('Welcome')
    body = _('''Greetings,

We would like to welcome you to %(service)s.

Here's a link to confirm your email address:

%(scheme)s://%(host)s/auth/confirm/%(token)s

Best regards.

--
%(service)s''', service=service, token=token, scheme=scheme, host=host)

    mail.send(Message(subject, body=body, recipients=[recipient]))


def send_confirmation(recipient, token):
    service = param('title', 'Diamond wiki')

    scheme = request.scheme
    host = request.host

    subject = _('Confirm your email address')
    body = _('''Greetings,

Here's a link to confirm your email address:

%(scheme)s://%(host)s/auth/confirm/%(token)s

Best regards.

--
%(service)s''', service=service, token=token, scheme=scheme, host=host)

    mail.send(Message(subject, body=body, recipients=[recipient]))
