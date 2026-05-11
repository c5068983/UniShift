from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from dotenv import load_dotenv
import os

load_dotenv()

# -------------------------------
# Generic email sender (SendGrid)
# -------------------------------
def send_email(subject, recipient, body):

    message = Mail(
        from_email="unishift.efssd@gmail.com",  # must be verified in SendGrid
        to_emails=recipient,
        subject=subject,
        plain_text_content=body
    )

    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        print("Email sent successfully:", response.status_code)

    except Exception as e:
        print("SendGrid error:", e)


# -------------------------------
# OTP EMAIL
# -------------------------------
def send_otp_email(email, otp):

    message = Mail(
        from_email="unishift.efssd@gmail.com",
        to_emails=email,
        subject="Your UniShift OTP Code",
        plain_text_content=f"""
Your OTP code is: {otp}

This code will expire in 5 minutes.

If you did not request this, ignore this email.
"""
    )

    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        print("OTP email sent:", response.status_code)

    except Exception as e:
        print("SendGrid error:", e)


# -------------------------------
# SHIFT EMAIL TEMPLATES
# -------------------------------
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