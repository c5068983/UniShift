from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class UpdateProfileForm(FlaskForm):
    username = StringField(
        'Username', 
        validators=[DataRequired(message="Username is required"),
                    Length(min=2, max=20, message="Username must be between 2 and 20 characters")])
    email = StringField("Email")
    mobile_number = StringField(
        'Mobile Number', 
        validators=[DataRequired(message="Mobile number is required"),
                    Length(min=10, max=15, message="Mobile number must be between 10 and 15 characters")])
    post_code = StringField(
        'Post Code', 
        validators=[DataRequired(message="Post code is required"),
                    Length(min=3, max=10, message="Post code must be between 3 and 10 characters")])
    profile_pic = FileField(
        'Profile Picture',
        validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')]
    )
    submit = SubmitField('Update Profile')