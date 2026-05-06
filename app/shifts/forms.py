from dataclasses import field

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateTimeField, DecimalField, ValidationError
from wtforms.validators import DataRequired, Length, NumberRange

class ShiftForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(message="Title is required"), Length(max=100,message="Title must be less than 100 characters")])
    job_description = TextAreaField('Job Description', validators=[Length(max=500,message="Job description must be less than 500 characters")])
    company_name = StringField('Company Name', validators=[DataRequired(message="Company name is required"), Length(max=100,message="Company name must be less than 100 characters")])
    city = StringField('City', validators=[DataRequired(message="City is required"), Length(max=100,message="City must be less than 100 characters")])
    post_code = StringField('Post Code', validators=[DataRequired(message="Post code is required"), Length(max=20,message="Post code must be less than 20 characters")])
    start_datetime = DateTimeField('Start Date and Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired(message="Start date and time is required")])
    end_datetime = DateTimeField('End Date and Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired(message="End date and time is required")])
    hourly_rate = DecimalField('Hourly Rate (£)', places=2, validators=[DataRequired(message="Hourly rate is required"), NumberRange(min=0,message="Hourly rate must be a positive number")])
    submit = SubmitField('Submit')
    
    # def validate_start_datetime(self, field):
    #     if field.errors:
    #         raise ValidationError(
    #             "Invalid datetime format. Use YYYY-MM-DDTHH:MM (example: 2026-04-28T14:30)"
    #         )
            
    # from wtforms import ValidationError

    # def validate_end_datetime(self, field):
    #     if not field.data:
    #         raise ValidationError(
    #             "Invalid datetime format. Use YYYY-MM-DDTHH:MM (example: 2026-04-28T14:30)"
    #         )