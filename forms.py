from email.policy import default
from typing import Optional
from flask_wtf import FlaskForm
from wtforms import *  # StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL, Email, Optional

from wtforms.fields.html5 import DateField, TimeField

from datetime import datetime

class TodoListForm(FlaskForm):
    todo = StringField(validators=[DataRequired()], render_kw={"placeholder": "New task here"})
    due_date = DateField(label="Due Date", validators=[DataRequired()], format='%Y-%m-%d', default=datetime.now())
    end_time = TimeField(label="end time", validators=[Optional()], format='%H:%M')
    complete = BooleanField(default=False, validators=[Optional()])
    important = BooleanField(default=False, validators=[Optional()])
    btn_add = SubmitField()
    btn_edit = SubmitField(label="Submit", render_kw=({'class':'btn btn-outline-primary btn-sm'}))
    btn_cancel = SubmitField(label='Cancel', render_kw={'formnovalidate':True,
                                                'class':'btn btn-outline-secondary btn-sm'})

class AlarmListForm(FlaskForm):
    alarm = StringField(label="Add reminder", validators=[DataRequired()])
    time = TimeField(label="Set timer", validators=[DataRequired()])
    submit = SubmitField(label="Submit")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()], render_kw={"placeholder": "Email"})
    password = PasswordField("Password", validators=[DataRequired()], render_kw={"placeholder": "Password"})
    name = StringField("Name", validators=[DataRequired()], render_kw={"placeholder": "Username"})
    submit = SubmitField("Sign Up", render_kw={'class':'btn btn-secondary'})

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()], render_kw={"placeholder": "Email"})
    password = PasswordField("Password", validators=[DataRequired()], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login", render_kw={'class':'btn btn-secondary'})
