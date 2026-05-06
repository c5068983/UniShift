from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler

from app.db.queries.shedular_queries import (
    auto_cancel_expired_shifts,
    auto_complete_expired_accepted_shifts,
    auto_reject_blocked_user_requests
)

scheduler = BackgroundScheduler()

def start_scheduler(app):

    # -----------------------
    # Cancel expired shifts
    # -----------------------
    def cancel_job():
        with app.app_context():
            print("⏰ Running cancel job...")
            auto_cancel_expired_shifts()

    scheduler.add_job(
        cancel_job,
        trigger='interval',
        minutes=15,
        id='auto_cancel_shifts',
        replace_existing=True,
        next_run_time=datetime.now(timezone.utc)
    )

    # -----------------------
    # Complete accepted shifts
    # -----------------------
    def complete_job():
        with app.app_context():
            print("⏰ Running complete job...")
            auto_complete_expired_accepted_shifts()
            
            
            
    def reject_blocked_user_requests():
        with app.app_context():
            print("⏰ Running reject blocked user requests job...")
            auto_reject_blocked_user_requests()

    scheduler.add_job(
        complete_job,
        trigger='interval',
        minutes=15,
        id='complete_shifts',
        replace_existing=True,
        max_instances=1,
        next_run_time=datetime.now(timezone.utc)
    )
    
    
    scheduler.add_job(
    reject_blocked_user_requests,
    trigger='interval',
    minutes=15,
    id='reject_blocked_requests',
    replace_existing=True,
    max_instances=1
)

    # -----------------------
    # Start scheduler safely
    # -----------------------
    if not scheduler.running:
        scheduler.start()
        print("🚀 Scheduler started")