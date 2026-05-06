
from .seed_users import seed_users
from .seed_shifts import seed_shifts
from .seed_history import seed_history
from .seed_requests import seed_requests

def run_all_seeds():
    seed_users()
    seed_shifts()
    seed_history()
    seed_requests()
