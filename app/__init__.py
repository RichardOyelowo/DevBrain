from flask_session import Session
from flask import Flask
from .config import Config
from .extensions import db as sa_db, mail, csrf, migrate, redis_client
from .db import close_db, ensure_database_ready, ensure_starter_catalog
from .routes import main
from .auth import auth
from .admin import admin
import os

if os.environ.get("FLASK_ENV") == "development":
    from dotenv import load_dotenv
    load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    sa_db.init_app(app)
    migrate.init_app(app, sa_db)
    mail.init_app(app)
    csrf.init_app(app)

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin)

    @app.context_processor
    def inject_current_user():
        from .models import User
        from flask import session

        user_id = session.get("user_id")
        return {"current_user": sa_db.session.get(User, user_id) if user_id else None}

    # helps with concurrency
    app.teardown_appcontext(close_db)

    @app.cli.command("init-db")
    def init_db_command():
        ensure_database_ready()
        print("Initialized DevBrain database and seed question bank.")

    @app.cli.command("ensure-catalog")
    def ensure_catalog_command():
        seeded = ensure_starter_catalog()
        if seeded:
            print("Seeded DevBrain starter catalog.")
        else:
            print("DevBrain starter catalog already exists.")

    # ------------------ Redis Session ------------------
    REDIS_URL = os.environ.get("REDIS_URL")
    if REDIS_URL:
        app.config['SESSION_TYPE'] = 'redis'
        app.config['SESSION_REDIS'] = redis_client
        app.config['SESSION_PERMANENT'] = False
        app.config['SESSION_USE_SIGNER'] = True
        Session(app)
        
    return app
