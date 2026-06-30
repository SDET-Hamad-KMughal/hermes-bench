import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Core architectural components
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    """Application Factory to configure and initialize HERMES-Bench."""
    app = Flask(__name__)
    
    # Fallback development secret key
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'hermes_secret_development_key_12345')
    
    # Standardize database path to 'instance/app.db'
    instance_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    db_path = os.path.join(instance_path, 'app.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.checkout import checkout_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(checkout_bp)

    return app