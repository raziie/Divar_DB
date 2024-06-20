from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email


class UserForm(FlaskForm):
    UserID = StringField('User ID', validators=[DataRequired()])
    IsActive = BooleanField('Is Active')
    FirstName = StringField('First Name', validators=[DataRequired()])
    LastName = StringField('Last Name', validators=[DataRequired()])
    RegisteredAt = StringField('Registered At', validators=[DataRequired()])
    Email = StringField('Email', validators=[DataRequired(), Email()])
    Phone = StringField('Phone', validators=[DataRequired()])
    City = StringField('City', validators=[DataRequired()])
    Street = StringField('Street', validators=[DataRequired()])
    House_num = StringField('House Number', validators=[DataRequired()])
    submit = SubmitField('Update')
