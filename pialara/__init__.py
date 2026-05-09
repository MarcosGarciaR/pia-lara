from flask import Flask, session, request
from flask_login import LoginManager
from pialara import db
from flask_babel import Babel, get_locale
import os
import json
import boto3
from botocore.exceptions import ClientError

def get_secrets():
    secret_name = "PIALARA"
    region_name = "us-east-1"  # ajusta a tu región

    client = boto3.client("secretsmanager", region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response["SecretString"])
    except ClientError as e:
        raise RuntimeError(f"Error al obtener secretos de AWS: {e}")

def create_app():
    app = Flask(__name__)

    secrets = get_secrets()

    app.config['PIALARA_DB_URI']          = secrets['PIALARA_DB_URI']
    app.config['PIALARA_DB_NAME']         = secrets['PIALARA_DB_NAME']
    app.config['SECRET_KEY']              = secrets['SECRET_KEY']
    app.config['BUCKET_NAME']             = secrets['BUCKET_NAME']
    app.config['GRADIO_URL']              = secrets['GRADIO_URL']

    app.config['LANGUAGES'] = ['es', 'en']
    app.config['BABEL_DEFAULT_LOCALE'] = 'es'
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

    def select_locale():
        return session.get('lang', 'es')

    babel = Babel(app, locale_selector=select_locale)

    @app.context_processor
    def inject_locale():
        return dict(get_locale=get_locale)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Blueprints
    from pialara.blueprints import auth, syllabus, users, audios, main, lara
    app.register_blueprint(auth.bp)
    app.register_blueprint(syllabus.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(audios.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(lara.bp)

    @login_manager.user_loader
    def load_user(user_id):
        return db.get_user_by_id(user_id)

    return app