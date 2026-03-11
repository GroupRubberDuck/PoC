from flask import Flask

from .routes import bp

def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(bp)

    app.secret_key = "TEST_KEY"
    return app
