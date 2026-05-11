from datetime import datetime

from app.auth import auth_bp
from app.utils.otp import generate_otp, verify_otp
from app.utils.email_helper import send_otp_email
from flask import app, request, request, session, url_for, render_template,flash, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from app.db.queries.auth_queries import create_user, get_user_by_email, update_user_password
from app.auth.forms import LoginForm, RegisterForm, ResetPasswordForm, ForgetPasswordForm, ResetPasswordForm
from app.utils import redirect_if_logged_in


@auth_bp.route('/login', methods=['GET', 'POST'])
@redirect_if_logged_in
def login():
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = get_user_by_email(form.email.data)
        if user and check_password_hash(user["password"], form.password.data):
            flash(category="success", message=f"Welcome back {user['username']}!")
            session['user_id'] = user['userId']
            session['role'] = user['role']
            session['status'] = "Active" if user['is_active'] else "Inactive"
            return redirect(url_for('main.index'))
        elif not user:
            flash(category="danger", message="User Does not Exist")
            return render_template('auth/login.html', form=form, title="Login")
        else:
            flash(category="danger", message="Login Failed: Invalid email or password")
            return render_template('auth/login.html', form=form, title="Login")
    else:
        return render_template('auth/login.html', form=form, title="Login")


@auth_bp.route('/register', methods=['GET', 'POST'])
@redirect_if_logged_in
def register():
    
    if "user_id" in session:
        flash(category="info", message="You are already logged in.")
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        if get_user_by_email(form.email.data):
            flash(category="danger", message="Registered Failed: Email already registered")
            return render_template('auth/register.html', form=form, title="Register")
        
        hashed_password = generate_password_hash(form.password.data)
        create_user(form.username.data, form.email.data, hashed_password, 'User')
        flash(category="success", message=f" Registration successful! welcome {form.username.data}")
        return redirect(url_for('auth.login'))
    else:
        return render_template('auth/register.html', form=form, title="Register")

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash(category="info", message="You have been logged out.")
    return redirect(url_for('auth.login'))

@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():

    if not session.get('user_id'):
        if not session.get("reset_verified"):
            return redirect(url_for("auth.login"))

    form = ResetPasswordForm()

    if form.validate_on_submit():

        hashed = generate_password_hash(form.password.data)

        user_id = session.get('reset_user_id')
        update_user_password(user_id, hashed)

        session.pop('reset_user_id', None)
        session.pop('reset_email', None)
        session.pop('reset_verified', None)

        flash("Password reset successful", "success")
        
        if session.get('user_id'):
            return redirect(url_for('main.profile'))
        
        
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form)
    
@auth_bp.route('/forget_password', methods=['GET', 'POST'])
def forget_password():
    form = ForgetPasswordForm()

    if form.validate_on_submit():
        user = get_user_by_email(form.email.data)

        if user:
            otp = generate_otp(user['email'])
            send_otp_email(user['email'], otp)

            session['reset_email'] = user['email']
            session['reset_otp_time'] = datetime.now().timestamp()   # ✅ FIX

            return redirect(url_for('auth.verify_reset_otp'))
        else:
            flash("No account found with that email.", "danger")

    return render_template('auth/forget_password.html', form=form)

@auth_bp.route('/login-otp', methods=['GET', 'POST'])
@redirect_if_logged_in
def login_otp():

    if request.method == 'POST':
        email = request.form['email']

        user = get_user_by_email(email)

        if not user:
            flash("User not found", "danger")
            return redirect(url_for('auth.login_otp'))

        otp = generate_otp(email)
        send_otp_email(email, otp)

        session['otp_email'] = email
        session['otp_time'] = datetime.now().timestamp()

        flash("OTP sent to your email", "info")
        return redirect(url_for('auth.verify_login_otp'))

    return render_template('auth/login_otp.html')


@auth_bp.route('/verify-login-otp', methods=['GET', 'POST'])
def verify_login_otp():

    if request.method == 'POST':
        user_otp = request.form['otp']
        email = session.get('otp_email')

        from app.utils.otp import verify_otp

        if verify_otp(email, user_otp):

            user = get_user_by_email(email)
            session['user_id'] = user['userId']

            session.pop('otp_email', None)
            session.pop('otp_time', None)

            flash("Login successful!", "success")
            return redirect(url_for('main.index'))

        else:
            flash("Invalid or expired OTP", "danger")

    return render_template('auth/verify_otp.html')

@auth_bp.route('/resend-otp')
def resend_otp():

    email = session.get('otp_email')
    last_sent = session.get('otp_time')

    if not email:
        return redirect(url_for('auth.login_otp'))

    now = datetime.now().timestamp()

    if last_sent and (now - last_sent < 60):
        remaining = int(60 - (now - last_sent))
        flash(f"Wait {remaining} seconds before resending OTP", "warning")
        return redirect(url_for('auth.verify_login_otp'))

    otp = generate_otp(email)
    send_otp_email(email, otp)

    session['otp_time'] = now

    flash("OTP resent successfully!", "success")
    return redirect(url_for('auth.verify_login_otp'))

@auth_bp.route('/verify-reset-otp', methods=['GET', 'POST'])
def verify_reset_otp():

    email = session.get('reset_email')

    if not email:
        return redirect(url_for('auth.forget_password'))

    if request.method == 'POST':

        otp = request.form['otp']

        if verify_otp(email, otp):

            user = get_user_by_email(email)

            session['reset_verified'] = True
            session['reset_user_id'] = user['userId']

            return redirect(url_for('auth.reset_password'))

        flash("Invalid OTP", "danger")

    return render_template('auth/verify_reset_otp.html')

@auth_bp.route('/resend-reset-otp')
def resend_reset_otp():

    # 🔐 use RESET session keys
    email = session.get('reset_email')
    last_sent = session.get('reset_otp_time')

    if not email:
        return redirect(url_for('auth.forget_password'))

    now = datetime.now().timestamp()

    # ⏱ cooldown logic
    if last_sent and (now - last_sent < 60):
        remaining = int(60 - (now - last_sent))
        flash(f"Wait {remaining} seconds before resending OTP", "warning")
        return redirect(url_for('auth.verify_reset_otp'))

    # 🔥 generate + send OTP
    otp = generate_otp(email)
    send_otp_email(email, otp)

    # update reset timer
    session['reset_otp_time'] = now

    flash("OTP resent successfully!", "success")
    return redirect(url_for('auth.verify_reset_otp'))