from flask import Flask
from flask_session import Session
from .routes import public, admin

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)
    app.register_blueprint(public.bp)
    app.register_blueprint(admin.bp)
    return app