from app.db.queries.history_queries import get_shift_history, log_shift_action,update_shift_history,get_accepted_shift_history
from app.db.queries.user_queries import get_user_by_id,change_rating_by_id,change_active_status_by_id
from app.shifts import shifts_bp
from app.db.queries.request_queries import create_shift_request, get_shift_request_by_id,update_shift_request_status_by_id,get_shift_requests,reject_other_requests,get_shift_request_by_other_id,get_accepted_shift_requests,cancel_all_request_by_shift_id
from flask import abort, render_template, request, session, g, flash, redirect, url_for
from datetime import datetime, timedelta
from app.db.queries.shift_queries import get_shift_by_id, update_shift_by_id, update_shift_status,create_shift,get_shift_by_id_with_poster,get_filtered_shifts
from app.shifts.forms import ShiftForm
from app.utils import login_required
from app.utils.decorators import active_user_required
from app.utils.email_helper import send_email, shift_withdrawn_email_body,shift_cancelled_email_body,shift_accepted_email_body

@shifts_bp.route('/available')
def available_shifts():

    city = request.args.get('city')
    post_code = request.args.get('post_code')
    order_by = request.args.get('order_by', 'time_asc')

    shifts = get_filtered_shifts(city, post_code, order_by,g.user['userId'] if g.user else None)

    return render_template("shifts/available_shifts.html", shifts=shifts)


@shifts_bp.route('/<int:shift_id>')
@login_required
def shift_detail(shift_id):
    shift = get_shift_by_id(shift_id);
    request = get_shift_request_by_other_id(shift_id, userId = session.get("user_id"))
    if not shift:
        return "Shift not found", 404
    return render_template("shifts/shift_detail.html", shift=shift, request=request)


@shifts_bp.route('/apply/<int:shift_id>')
@login_required
@active_user_required
def apply(shift_id):

    shift = get_shift_by_id(shift_id)
    request = get_shift_request_by_other_id(shift_id, userId = session.get("user_id"))
    
    if request and request["status"] == "Pending":
        flash("You have already applied for this shift. Please wait for the poster to respond.", "warning")
        return render_template("shifts/shift_detail.html", shift=shift, request=request)    
    
    if request and request["status"] == "Rejected":
        flash("Your previous application for this shift was Rejected. You cannot apply again.", "danger")
        return render_template("shifts/shift_detail.html", shift=shift, request=request)
    
    if request and request["status"] == "Accepted":
        flash("You have already been Accepted for this shift. Please check your dashboard for details.", "success")
        return render_template("shifts/shift_detail.html", shift=shift, request=request)
    
    if request and request["status"] == "Withdrawn":
        flash("Your previous application for this shift was Withdrawn. You cannot apply again.", "danger")
        return render_template("shifts/shift_detail.html", shift=shift, request=request)

    if not shift:
        return "Shift not found", 404

    if shift["status"] != "Open":
        return "Shift not available", 400

    user_id = session.get("user_id");
    
    shift_request = create_shift_request(shift_id, userId=user_id)
    return render_template("shifts/shift_detail.html", shift=shift, request = shift_request)

@shifts_bp.route('/withdraw/<int:shift_id>/<int:request_id>')
@login_required
def withdraw(shift_id, request_id):
    shift = get_shift_by_id_with_poster(shift_id)
    request = get_shift_request_by_id(request_id)

    if not shift:
        return "Shift not found", 404
    
    if request["requesterId"] != g.user['userId']:
        return "Unauthorized", 403
    
    if request["status"] == "Accepted":
        rating = change_rating_by_id(request["requesterId"], -10)
        if rating < 50 and request['role'] != "Admin":
            change_active_status_by_id(request["requesterId"], False)
        history = get_shift_history(shift_id, status="Accepted", userId=g.user['userId'])
        update_shift_history(history['historyId'], "Withdrawn")
        send_email(
            "Shift has been Withdrawn ⚠️",
            shift["poster_email"],
            shift_withdrawn_email_body(shift)
        )
    flash("Your application has been withdrawn.", "info")
    shift = update_shift_status(shift_id, "Open")
    request = update_shift_request_status_by_id(request_id, "Withdrawn")
    return render_template("shifts/shift_detail.html", shift=shift, request=request)

@shifts_bp.route('/add', methods=['GET', 'POST'])
@login_required
@active_user_required
def add_shift():
    form = ShiftForm()

    if form.validate_on_submit():

        start = form.start_datetime.data
        end = form.end_datetime.data
        now = datetime.now()

        # ----------------------------
        # RULE 1: Start must be 24h ahead
        # ----------------------------
        if start < now + timedelta(hours=24):
            flash("Shift must start at least 24 hours from now", "danger")
            return render_template("shifts/add_shift.html", form=form)

        # ----------------------------
        # RULE 2: End must be after start
        # ----------------------------
        if end <= start:
            flash("End time must be after start time", "danger")
            return render_template("shifts/add_shift.html", form=form)

        if end < now:
            flash("End time cannot be in the past", "danger")
            return render_template("shifts/add_shift.html", form=form)

        flash("Shift created successfully!", "success")
        shift = create_shift(
            user_id=g.user['userId'],
            title=form.title.data,
            job_description=form.job_description.data,
            company_name=form.company_name.data,
            city=form.city.data,
            post_code=form.post_code.data,
            hourly_rate=float(form.hourly_rate.data),
            start_datetime=start.strftime('%Y-%m-%d %H:%M:%S'),
            end_datetime=end.strftime('%Y-%m-%d %H:%M:%S')
        )
        
        return render_template("shifts/shift_detail.html", shift=shift)

    return render_template("shifts/add_shift.html", form=form)

@shifts_bp.route('/cancel/<int:shift_id>')
@login_required
@active_user_required
def cancel_shift(shift_id):
    shift = get_shift_by_id(shift_id)
    
    if not shift:
        return "Shift not found", 404
    
    if shift["userId"] != g.user['userId'] and g.user['role'] != "Admin":
        return "Unauthorized", 403
    
    request = get_accepted_shift_requests(shift_id)
    history = get_accepted_shift_history(shift_id)
    
    if request or history:
        print(request['status'])
        update_shift_request_status_by_id(request["requestId"], "Rejected")
        if shift['role'] != "Admin":
            rating = change_rating_by_id(shift['userId'], -10)
            if rating < 50:
                if rating < 0:
                    rating = 0
                change_active_status_by_id(shift['userId'], False)
        update_shift_history(history['historyId'], "Cancelled")
        send_email(
            "Shift Cancelled ⚠️",
            history["user_email"],
            shift_cancelled_email_body(history, shift)
        )
    cancel_all_request_by_shift_id(shift_id)
    update_shift_status(shift_id, "Cancelled")
    flash("Shift cancelled successfully by " + g.user['username'] + ".", "info")
    if session['role'] == "Admin":
        return redirect(url_for('shifts.available_shifts'))
    return redirect(url_for('main.poster_dashboard'))

@shifts_bp.route('/show_requests/<int:shift_id>')
@login_required
def show_requests(shift_id):
    shift = get_shift_by_id(shift_id)
    if not shift:
        return "Shift not found", 404

    if shift["userId"] != g.user['userId'] and g.user['role'] != "Admin":
        return "Unauthorized", 403

    requests = get_shift_requests(shift_id,'Pending')
    return render_template("shifts/requests.html", shift=shift, requests=requests)

@shifts_bp.route('/update_request_status/<int:shift_id>/<int:request_id>/<string:new_status>')
@login_required
def update_request_status(shift_id, request_id=None, new_status=None):
    shift = get_shift_by_id(shift_id)
    request = get_shift_request_by_id(request_id)
    user = get_user_by_id(request["requesterId"])

    if not shift or not request:
        return "Shift or request not found", 404

    if shift["userId"] != g.user['userId']:
        return "Unauthorized", 403

    if new_status == "Accepted":
        shift = update_shift_status(shift_id, "Accepted")
        poster = get_user_by_id(shift["userId"])
        log_shift_action(shift_id, request["requesterId"], "Accepted")
        reject_other_requests(shift_id, request_id)
        send_email(
            "Shift Accepted 🎉",
            user["email"],
            shift_accepted_email_body(user, shift, poster)
        )        
    update_shift_request_status_by_id(request_id, new_status)
    
    return redirect(url_for('shifts.show_requests', shift_id=shift_id))

@shifts_bp.route('/edit/<int:shift_id>', methods=['GET', 'POST'])
@login_required
def edit_shift(shift_id):
    form = ShiftForm()

    # Fetch existing shift
    shift = get_shift_by_id(shift_id)
    
    if shift and shift["userId"] != g.user['userId']:
        return "Unauthorized", 403

    if not shift:
        flash("Shift not found", "danger")
        return redirect(url_for('shifts.dashboard'))

    # ----------------------------
    # PRE-FILL FORM ON GET
    # ----------------------------
    if request.method == 'GET':
        form.title.data = shift['title']
        form.company_name.data = shift['company_name']
        form.city.data = shift['city']
        form.post_code.data = shift['post_code']
        form.hourly_rate.data = shift['hourly_rate']
        form.job_description.data = shift['job_description']

        # convert string -> datetime-local format
        form.start_datetime.data = datetime.strptime(
            shift['start_datetime'], '%Y-%m-%d %H:%M:%S'
        )

        form.end_datetime.data = datetime.strptime(
            shift['end_datetime'], '%Y-%m-%d %H:%M:%S'
        )

        return render_template("shifts/edit_shift.html", form=form, shift=shift)

    # ----------------------------
    # VALIDATE FORM ON POST
    # ----------------------------
    if form.validate_on_submit():

        start = form.start_datetime.data
        end = form.end_datetime.data
        now = datetime.now()

        # RULE 1: Start must be 24h ahead
        if start < now + timedelta(hours=24):
            flash("Shift must start at least 24 hours from now", "danger")
            return render_template("shifts/edit_shift.html", form=form, shift=shift)

        # RULE 2: End must be after start
        if end <= start:
            flash("End time must be after start time", "danger")
            return render_template("shifts/edit_shift.html", form=form, shift=shift)

        # RULE 3: End cannot be in past
        if end < now:
            flash("End time cannot be in the past", "danger")
            return render_template("shifts/edit_shift.html", form=form, shift=shift)

        # ----------------------------
        # UPDATE SHIFT
        # ----------------------------
        update_shift_by_id(
            shift_id=shift_id,
            title=form.title.data,
            job_description=form.job_description.data,
            company_name=form.company_name.data,
            city=form.city.data,
            post_code=form.post_code.data,
            hourly_rate=float(form.hourly_rate.data),
            start_datetime=start.strftime('%Y-%m-%d %H:%M:%S'),
            end_datetime=end.strftime('%Y-%m-%d %H:%M:%S')
        )

        flash("Shift updated successfully!", "success")

        updated_shift = get_shift_by_id(shift_id)
        return render_template("shifts/shift_detail.html", shift=updated_shift)

    return render_template("shifts/edit_shift.html", form=form, shift=shift)

@shifts_bp.route('/cancel_request/<int:shift_id>/<int:request_id>')
@login_required
def cancel_request(shift_id, request_id):

    return redirect(url_for(
        'shifts.update_request_status',
        shift_id=shift_id,
        request_id=request_id,
        new_status="Withdrawn"
    ))
    