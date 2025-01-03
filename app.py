from flask import Flask
from application.database import db
from application.api import api, Section
from application.config import login_manager

app = None

def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///lms.sqlite3"
    db.init_app(app)
    api.init_app(app)

    app.config["SECRET_KEY"] = "kjhfwJHFwhiohfnwewUGUIwhjlwjwkeIbjkwejIwkeijdInemUF"
    login_manager.init_app(app)

    app.app_context().push()
    return app

app = create_app()

from application.controllers import *


if __name__ == "__main__":
    app.run()