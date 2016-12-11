#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, redirect, flash, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from .forms import LoginForm, LogonForm, EditForm
from .models import User
from datetime import datetime


@lm.user_loader
def load_user(id):
    u = User.query.get(int(id))
    app.logger.info("load user, u: %r, type: %s" % (u, type(u)))
    return u


def after_logon(form):
    app.logger.info(form.nickname.data)
    app.logger.info(form.email.data)
    app.logger.info(form.password.data)
    user = User(nickname=form.nickname.data,
                email=form.email.data,
                password=form.password.data)
    db.session.add(user)
    db.session.commit()
    db.sessin.add(user.follow(user))
    db.session.commit()


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()


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
        after_logon(form)
        return redirect(url_for('login'))

    return render_template('logon.html',
                           title="Logon",
                           form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<nickname>')
@login_required
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for(index))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'},
    ]
    return render_template(
        'user.html',
        user=user,
        posts=posts)


@app.route("/edit", methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your change have been saved.')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form)


@app.errorhandler(404)
def internal_error_404(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error_500(error):
    db.session.rollback()
    return render_template('500.html'), 400
