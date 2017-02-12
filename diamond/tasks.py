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

import traceback

from celery import Celery
from flask import g
from flask_babel import gettext as _
from flask_mail import Message
from flask_babel import refresh

from diamond.app import app
from diamond.mail import mail, with_mail
from diamond.models import param
from diamond.emails import (
    EMAIL_WELCOME, EMAIL_CONFIRMATION, EMAIL_MODIFIED
)

celery = Celery('tasks', broker=app.config['REDIS_URL'])


def with_celery():
    return 'mock' not in app.config['REDIS_URL']


def send_email(context, subject, body, params):
    if not with_mail():
        return

    recipients = [
        context['user']['email']
    ]

    params.update({
        'scheme': context['scheme'],
        'host': context['host'],
        'service': param('title', 'Diamond wiki')
    })

    with app.app_context():
        g.locale = context['locale']

        refresh()

        subject = _(subject)
        body = _(body.strip(), **params)

        message = Message(subject, recipients, body)

        try:
            mail.send(message)
        except:
            app.logger.error(
                traceback.format_exc().strip()
            )


@celery.task
def send_welcome(context, token):
    subject = 'Welcome'
    send_email(context, subject, EMAIL_WELCOME, {
        'token': token
    })


@celery.task
def send_confirmation(context, token):
    subject = 'Confirm your email address'
    send_email(context, subject, EMAIL_CONFIRMATION, {
        'token': token
    })


@celery.task
def send_modified(context, slug):
    subject = 'A page has been modified'
    send_email(context, subject, EMAIL_MODIFIED, {
        'slug': slug
    })
