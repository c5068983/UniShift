from flask import Flask, session, g
from app.db.queries.user_queries import get_user_by_id
from flask_mail import Mail
from app.utils.scheduler import start_scheduler
import os

mail = Mail()

def create_app():
    app = Flask(__name__)

    # -------------------
    # BASIC CONFIG
    # -------------------
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SITE_NAME'] = "Unishift"

    @app.context_processor
    def inject_globals():
        return dict(site_name=app.config['SITE_NAME'])

    # -------------------
    # MAIL CONFIG
    # -------------------
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False

    app.config['MAIL_USERNAME'] = 'unishift.efssd@gmail.com'
    app.config['MAIL_PASSWORD'] = 'kzre yhad zwsb rlqi'
    app.config['MAIL_DEFAULT_SENDER'] = 'unishift.efssd@gmail.com'

    mail.init_app(app)

    # -------------------
    # BLUEPRINTS
    # -------------------
    from app.auth import auth_bp
    from app.shifts import shifts_bp
    from app.main import main_bp
    from app.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(shifts_bp, url_prefix='/shifts')
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # -------------------
    # USER LOADING
    # -------------------
    @app.before_request
    def load_user():
        user_id = session.get('user_id')
        if user_id:
            g.user = get_user_by_id(user_id)
        else:
            g.user = None
            
    # -------------------
    # START SCHEDULER
    # -------------------
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        start_scheduler(app)

    return app