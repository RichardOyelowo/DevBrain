from flask import Flask
from .config import Config
from .extensions import mail, csrf
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

    return app