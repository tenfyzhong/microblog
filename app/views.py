#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, redirect, flash, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from .forms import LoginForm, LogonForm
from .models import User


@lm.user_loader
def load_user(id):
    u = User.query.get(int(id))
    app.logger.info("load user, u: %r, type: %s" % (u, type(u)))
    return u


@app.before_request
def before_request():
    g.user = current_user


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = g.user
    posts = [
        {
            'author': {'nickname': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'nickname': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template(
        "index.html",
        title="Home",
        user=user,
        posts=posts)


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    app.logger.info('method ' + request.method)
    if request.method == 'GET':
        if g.user is not None and g.user.is_authenticated:
            return redirect(url_for('index'))
    form = LoginForm()
    app.logger.info(form)
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        app.logger.info(form.openid.data)
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    return render_template('login.html',
                           next=oid.get_next_url(),
                           title='Sign In',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])


@app.route('/logon', methods=['GET', 'POST'])
def logon():
    form = LogonForm()
    if form.validate_on_submit():
        app.logger.info(form.nickname.data)
        app.logger.info(form.email.data)
        app.logger.info(form.password.data)
        # TODO added by tenfy 2016-12-10 18:11 add to db
        user = User(nickname=form.nickname.data,
                    email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('logon.html',
                           title="Logon",
                           form=form)


@oid.after_login
def after_login(resp):
    app.logger.info('resp %r' % resp)
    if resp.email is None or resp.email == "":
        flash('Invalid login, Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = User(nickname=nickname, email=resp.email)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/error')
def error():
    return render_template("error.html")
