from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config.Config")

    CORS(app)

    db_type = app.config["DB_TYPE"]

    if db_type == "sql":
        db.init_app(app)
        with app.app_context():
            from app import models  # Ensure SQLAlchemy model metadata is registered

            db.create_all()
    else:
        import pymongo

        client = pymongo.MongoClient(app.config["MONGO_URI"])
        app.mongo_db = client[app.config["MONGO_DB_NAME"]]

    from app.controllers.main import bp

    app.register_blueprint(bp)

    return app
