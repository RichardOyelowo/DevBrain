from flask_session import Session
from flask import Flask
from .config import Config
from .extensions import mail, csrf, redis_client
from .db import close_db
from .routes import main
from .auth import auth
import os

if os.environ.get("FLASK_ENV") == "development":
    from dotenv import load_dotenv
    load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    mail.init_app(app)
    csrf.init_app(app)

    app.register_blueprint(main)
    app.register_blueprint(auth)

    # helps with concurrency
    app.teardown_appcontext(close_db)

    # ------------------ Redis Session ------------------
    REDIS_URL = os.environ.get("REDIS_URL")
    if REDIS_URL:
        app.config['SESSION_TYPE'] = 'redis'
        app.config['SESSION_REDIS'] = redis_client
        app.config['SESSION_PERMANENT'] = False
        app.config['SESSION_USE_SIGNER'] = True
        Session(app)
        
    return app