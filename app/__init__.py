from flask import Flask
from .routes import admin, public


def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # Suporte a sessões
    from flask_session import Session
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)

    app.register_blueprint(public.bp)
    app.register_blueprint(admin.bp)
    return app