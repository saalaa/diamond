from flask import request, render_template, redirect, url_for, flash

from slugify import slugify
from flask_login import LoginManager, login_user, logout_user, current_user, \
        AnonymousUserMixin

from app import app
from db import db
from model_user import User
from model_document import Document
from maths import hash, generate

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
        return respond('You failed to answer the simple maths question')

    if User.exists(slug):
        return respond('This user name is unavailable')

    is_first = User.is_first()
    page = Document.get(slug)

    if not page.id:
        page.title = name
        page.save()

    user = User(slug=slug, admin=is_first)
    user.set_password(password)

    user.save()

    db.session.commit()

    login_user(user)

    return redirect(url_for('read', name=slug))

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
        return respond('Wrong user name or password')

    login_user(user)

    return redirect(url_for('read', name=user.slug))

@app.route('/sign-out')
def sign_out():
    logout_user()
    return redirect(url_for('read'))
