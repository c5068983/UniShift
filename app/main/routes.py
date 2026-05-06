import os
from werkzeug.utils import secure_filename
from flask import flash, redirect, render_template, g, url_for
from app.main import main_bp
from app.main.forms import UpdateProfileForm
from app.utils import login_required
from app.db.queries.user_queries import update_user_by_id
from app.db.queries.shift_queries import get_all_posted_shifts_by_user_id_other_than_status,get_shifts_by_user_id
from app.db.queries.request_queries import get_shift_requests_by_user_id
from flask import current_app, request

from app.utils.email_helper import send_email  


# Home page
@main_bp.route('/')
def index():
    return render_template('main/home.html')

@main_bp.route('/about')
def about():
    return render_template('main/about.html')


@main_bp.route('/profile')
@login_required
def profile():
    return render_template('main/profile.html', title="Profile", user=g.user)

@main_bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():

    form = UpdateProfileForm()

    if request.method == "GET":
        form.username.data = g.user["username"]
        form.mobile_number.data = g.user["mobile_number"]
        form.post_code.data = g.user["post_code"]

    if form.validate_on_submit():

        filename = g.user["profile_picture"] or "default_profile.png"
        if form.profile_pic.data:
            file = form.profile_pic.data
            filename = secure_filename(file.filename)

            upload_folder = os.path.join(
                current_app.root_path,
                'static',
                'uploads'
            )

            os.makedirs(upload_folder, exist_ok=True)

            upload_path = os.path.join(upload_folder, filename)
            file.save(upload_path)

        update_user_by_id(
            g.user['userId'],
            form.username.data,
            form.mobile_number.data,
            form.post_code.data,
            filename
        )

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))

    return render_template(
        'main/edit_profile.html',
        form=form,
        user=g.user,
        title="Edit Profile"
    )
    
@main_bp.route('/poster_dashboard')
@login_required
def poster_dashboard():
    
    shifts = get_all_posted_shifts_by_user_id_other_than_status(g.user['userId'], 'Cancelled')
    
    return render_template("main/poster.html", shifts=shifts)

@main_bp.route('/contact')
def contact():
    return render_template("main/contact.html")

@main_bp.route('/dashboard')
@main_bp.route('/dashboard/<int:user_id>')
@login_required
def user_dashboard(user_id=None):

    if user_id is None:
        user_id = g.user['userId']
        
    if user_id != g.user['userId'] and g.user['role'] != 'Admin':
        flash("You are not authorized to view others dashboard", "danger")
        return redirect(url_for('main.user_dashboard'))
    
    requests = get_shift_requests_by_user_id(user_id, 'Pending')
    Accepted = get_shift_requests_by_user_id(user_id, 'Accepted')
    withdrawn = get_shift_requests_by_user_id(user_id, 'Withdrawn')
    rejected = get_shift_requests_by_user_id(user_id, 'Rejected')
    
    # merge properly
    withdrawn.extend(rejected)

    return render_template(
        'main/dashboard.html',
        requests=requests,
        Accepted=Accepted,
        withdrawn=withdrawn
    )

@main_bp.route('/test-email')
def test_email():
    send_email(
        "Test Email",
        "nokeshkola143@gmail.com",
        "Flask email is working!"
    )
    return "Email sent!"

@main_bp.route('/blocked')
def account_blocked():
    return render_template("main/block.html")