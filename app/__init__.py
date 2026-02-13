from flask import Flask, request, render_template, redirect, url_for, session
from app.utils import calculate_grade, save_quiz_result
from app.auth import login_required, get_db, auth
from config import SECRET_KEY, DATABASE_URL
from flask_wtf import CSRFProtect
from question import Questions
from app.routes import appp
import os



def create_app():
    app = Flask(__name__)

    csrf = csrf.init_app(app)

    # Registering auth routes
    app.register_blueprint(appp)
    app.register_blueprint(auth)

    csrf.exempt(auth)

    csrf = CSRFProtect(app)

    app.secret_key = SECRET_KEY

    # Session config
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=True,
    )

    return app

