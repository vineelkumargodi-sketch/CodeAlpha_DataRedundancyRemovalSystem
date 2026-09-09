from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os


db = SQLAlchemy()


def create_app():
    load_dotenv()

    # Project root:
    # D:\CodeAlpha_DataRedundancyRemovalSystem
    project_root = Path(__file__).resolve().parent.parent

    template_folder = project_root / "templates"
    static_folder = project_root / "static"

    app = Flask(
        __name__,
        template_folder=str(template_folder),
        static_folder=str(static_folder),
        instance_relative_config=True
    )

    # Make sure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + str(
            Path(app.instance_path) / "redundancy.db"
        )
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize database
    db.init_app(app)

    # Import models
    from app.models import (
        Record,
        DuplicateAttempt,
        ValidationLog
    )

    # Register API routes
    from app.routes.records import records_bp

    app.register_blueprint(
        records_bp,
        url_prefix="/api"
    )

    # Home page
    @app.get("/")
    def home():
        return render_template("index.html")

    # Health check
    @app.get("/health")
    def health():
        return {
            "status": "healthy"
        }

    # Create database tables
    with app.app_context():
        db.create_all()

    return app