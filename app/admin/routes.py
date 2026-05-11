from datetime import datetime, datetime, timedelta
from app.admin import admin_bp
from app.db.queries.shift_queries import get_all_shifts
from app.utils.decorators import admin_required
from flask import redirect, request, url_for, render_template
from app.db.queries.user_queries import get_all_users_exclude_admins, change_active_status_by_id, get_user_by_id
from app.db.queries.history_queries import get_all_shift_history

@admin_bp.route('/users')
@admin_required
def users_dashboard():

    search = request.args.get("search")
    status = request.args.get("status")
    min_rating = request.args.get("min_rating")
    max_rating = request.args.get("max_rating")

    # -----------------------------
    # 1. Base dataset
    # -----------------------------
    users = get_all_users_exclude_admins()

    # -----------------------------
    # 2. SEARCH filter
    # -----------------------------
    if search:
        users = [
            u for u in users
            if search.lower() in u['username'].lower()
            or search.lower() in u['email'].lower()
        ]

    # -----------------------------
    # 3. STATUS filter
    # -----------------------------
    if status == "active":
        users = [u for u in users if u['is_active'] == 1]

    elif status == "blocked":
        users = [u for u in users if u['is_active'] == 0]

    # -----------------------------
    # 4. RATING filters
    # -----------------------------
    if min_rating:
        users = [u for u in users if u['rating_points'] >= int(min_rating)]

    if max_rating:
        users = [u for u in users if u['rating_points'] <= int(max_rating)]

    # -----------------------------
    # 5. Analytics (based on filtered users OR all users — your choice)
    # -----------------------------
    cutoff_date = datetime.now() - timedelta(days=30)

    active_users = sum(1 for user in users if user['is_active'])
    inactive_users = len(users) - active_users

    low_rating_users = sum(
        1 for user in users if user['rating_points'] < 50
    )

    new_users_month = 0

    for user in users:
        created_at = user['created_at']

        if isinstance(created_at, str):
            try:
                created_at = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue

        if created_at >= cutoff_date:
            new_users_month += 1

    # -----------------------------
    # 6. Render
    # -----------------------------
    return render_template(
        'admin/users.html',
        users=users,
        active_users=active_users,
        inactive_users=inactive_users,
        low_rating_users=low_rating_users,
        new_users_month=new_users_month
    )

@admin_bp.route('/block-user/<int:user_id>')
@admin_required
def block_user(user_id):
    change_active_status_by_id(user_id,is_active=False)
    return redirect(url_for('admin.users_dashboard'))

@admin_bp.route('/unblock-user/<int:user_id>')
@admin_required
def unblock_user(user_id):
    change_active_status_by_id(user_id,is_active=True)
    return redirect(url_for('admin.users_dashboard'))

@admin_bp.route('/shifts')
@admin_required
def shifts_dashboard():
    
    shifts = get_all_shifts()
    history = get_all_shift_history(10)
    open_shifts = sum(1 for shift in shifts if shift['status'] == 'Open')
    completed_shifts = sum(1 for shift in shifts if shift['status'] == 'Completed')
    accepted_shifts = sum(1 for shift in shifts if shift['status'] ==  'Accepted')
    return render_template('admin/shifts.html', open_shifts=open_shifts, completed_shifts=completed_shifts, accepted_shifts=accepted_shifts, history=history)

@admin_bp.route('/user/<int:user_id>/dashboard/')
@admin_required
def user_dashboard(user_id):
    user = get_user_by_id(user_id)

    if not user:
        return redirect(url_for('admin.users_dashboard'))

    return redirect(url_for('main.user_dashboard', user_id=user_id))