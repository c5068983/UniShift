from functools import wraps
from flask import session, redirect, url_for, flash

from app.db.queries.user_queries import get_user_by_id

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def role_required(role):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                flash("Please login first", "warning")
                return redirect(url_for("auth.login"))

            if session.get("role") != role:
                flash("Access denied", "danger")
                return redirect(url_for("main.index"))

            return f(*args, **kwargs)
        return decorated_function
    return wrapper

from functools import wraps
from flask import session, redirect, url_for

def active_user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")

        if not user_id:
            return redirect(url_for("auth.login"))

        user = get_user_by_id(user_id)

        # If user not found or inactive
        if not user or not user["is_active"]:
            session.clear()
            return redirect(url_for("main.account_blocked"))
        return f(*args, **kwargs)

    return decorated_function

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("role") != "Admin":
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return wrapper


def redirect_if_logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" in session:
            flash(category="info", message="You are already logged in.")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated_function