from flask import Flask
from dotenv import load_dotenv
from pathlib import Path

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

    from .routes import bp
    app.register_blueprint(bp)
    return app
