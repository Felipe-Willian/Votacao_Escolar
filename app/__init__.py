from flask import Flask
from .routes import admin, public


def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    app.register_blueprint(public.bp)
    app.register_blueprint(admin.bp)

    return app