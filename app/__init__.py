import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config_by_name

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_name=None):
    """Application factory method to configure and instantiate the Flask app."""
    if not config_name:
        config_name = os.environ.get('FLASK_ENV', 'development')
        
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))
    
    # Initialize extensions with app context
    db.init_app(app)
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # Configure logging
    setup_logging(app)
    
    # Ensure directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['NLTK_DATA_DIR'], exist_ok=True)
    
    # Configure NLTK path and auto-download resources
    from app.utils.nltk_helper import init_nltk_resources
    init_nltk_resources(app.config['NLTK_DATA_DIR'])
    
    # Register Blueprints
    from app.auth.routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from app.dashboard.routes import dashboard as dashboard_blueprint
    app.register_blueprint(dashboard_blueprint)
    
    from app.resume.routes import resume as resume_blueprint
    app.register_blueprint(resume_blueprint, url_prefix='/resume')
    
    from app.interview.routes import interview as interview_blueprint
    app.register_blueprint(interview_blueprint, url_prefix='/interview')
    
    from app.skill_gap.routes import skill_gap as skill_gap_blueprint
    app.register_blueprint(skill_gap_blueprint, url_prefix='/skill_gap')
    
    from app.readiness.routes import readiness as readiness_blueprint
    app.register_blueprint(readiness_blueprint, url_prefix='/readiness')
    
    # Register error handlers
    register_error_handlers(app)
    
    return app

def setup_logging(app):
    """Sets up application-level logging."""
    log_level = logging.INFO
    if app.config.get('DEBUG'):
        log_level = logging.DEBUG
        
    handlers = [
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(app.config['UPLOAD_FOLDER'], '../app.log'))
    ]
    
    # Enable CloudWatch Logging (failsafe check)
    try:
        from app.utils.logger import CloudWatchLogHandler
        cw_handler = CloudWatchLogHandler(
            log_group="AI-Career-Assistant-Logs",
            log_stream="AppServer",
            config=app.config
        )
        cw_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        ))
        # Stream warnings & errors to CloudWatch to save bandwidth
        cw_handler.setLevel(logging.WARNING)
        handlers.append(cw_handler)
    except Exception as e:
        app.logger.warning(f"Could not load CloudWatch logger: {str(e)}")
        
    logging.basicConfig(
        level=log_level,
        format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        handlers=handlers
    )
    app.logger.info("Application logging initialized.")

def register_error_handlers(app):
    """Registers standard HTTP error handlers."""
    from flask import render_template
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
        
    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f"Internal Server Error: {str(e)}")
        return render_template('errors/500.html'), 500
