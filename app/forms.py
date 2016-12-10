#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import DataRequired


class LoginForm(Form):
    openid = StringField('openid', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)


class LogonForm(Form):
    nickname = StringField('nickname', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password',
                             validators=[DataRequired()])
