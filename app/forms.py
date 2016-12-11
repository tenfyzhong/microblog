#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms import StringField, BooleanField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length


class LoginForm(Form):
    nickname = StringField('nickname', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)


class LogonForm(Form):
    nickname = StringField('nickname', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password',
                             validators=[DataRequired()])


class EditForm(Form):
    nickname = StringField('nickname', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])
