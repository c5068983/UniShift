import random
from datetime import datetime, timedelta

otp_store = {}

def generate_otp(email):
    otp = str(random.randint(100000, 999999))

    otp_store[email] = {
        "otp": otp,
        "expires": datetime.now() + timedelta(minutes=5)
    }

    return otp


def verify_otp(email, user_otp):
    if email not in otp_store:
        return False

    data = otp_store[email]

    if datetime.now() > data["expires"]:
        del otp_store[email]
        return False

    if data["otp"] == user_otp:
        del otp_store[email]
        return True

    return False