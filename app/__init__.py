from flask import Flask
from app.routes.auth_routes import auth
from app.routes.market_routes import market
from app.routes.profile_routes import profile
from app.routes.advertise_routes import ad
from app.routes.admin_routes import admin
import os


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config')

    # # Initialize utils
    # redis_client.init_app(app)
    app.secret_key = os.getenv('SECRET_KEY')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(market, url_prefix='/market')
    app.register_blueprint(profile, url_prefix='/profile')
    app.register_blueprint(ad, url_prefix='/ad')
    app.register_blueprint(admin, url_prefix='/admin')
    return app
