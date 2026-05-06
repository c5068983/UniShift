from flask_mail import Message
from app import mail

def send_email(subject, recipient, body):
    msg = Message(
        subject=subject,
        recipients=[recipient],
        body=body
    )
    mail.send(msg)
    
def shift_withdrawn_email_body(shift):
    return f"""
    Hi {shift['poster_name']},

    Your shift has been withdrawn.

    Shift: {shift['title']}
    Company: {shift['company_name']}
    """
    
def shift_cancelled_email_body(history, shift):
    return f"""
    Hi {history['user_name']},

    Your shift has been cancelled by the Poster.

    Shift: {shift['title']}
    Company: {shift['company_name']}
    """
    
def shift_accepted_email_body(user, shift, poster):
    return f"""
Hi {user['username']},

Your shift has been ACCEPTED.

Title: {shift['title']}
Company: {shift['company_name']}
Location: {shift['city']}
Start: {shift['start_datetime']}
End: {shift['end_datetime']}
Post Code: {shift['post_code']}
""" + (
        f"""
Poster Details:
Name: {poster['username']}
Email: {poster['email']}
""" if poster else ""
    ) + """

Please make sure to show up on time and contact the poster if you have any questions.

— UniShift Team
"""


from flask_mail import Message
from flask import current_app
from app import mail

def send_otp_email(email, otp):

    msg = Message(
        subject="Your UniShift OTP Code",
        recipients=[email]
    )

    msg.body = f"""
Your OTP code is: {otp}

This code will expire in 5 minutes.

If you did not request this, ignore this email.
"""

    mail.send(msg)