from flask import Flask
from pymongo import MongoClient
from .routes import bp

def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = "TEST_KEY"

    app.mongodb_client = MongoClient("mongodb://root:grouprubberduckpoc2026@localhost:27017/", serverSelectionTimeoutMS=2000)
    app.db = app.mongodb_client["poc_db"]

    app.register_blueprint(bp)

    return app
