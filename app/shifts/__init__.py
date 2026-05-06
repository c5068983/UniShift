from flask import Blueprint

shifts_bp = Blueprint('shifts', __name__)

from app.shifts import routes