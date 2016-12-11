#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, redirect, flash, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm
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
def login():
    app.logger.info('method ' + request.method)
    if request.method == 'GET':
        if g.user is not None and g.user.is_authenticated:
            return redirect(url_for('index'))
    form = LoginForm()
    app.logger.info(form)
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        user = User.query.filter_by(nickname=form.nickname.data).first()
        if user is not None:
            # had logon
            if user.password == form.password.data:
                login_user(user, remember=form.remember_me.data)
                return redirect(url_for('index'))
            else:
                flash("password error")
        else:
            flash("has not registe")
    return render_template('login.html',
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


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/error')
def error():
    return render_template("error.html")
