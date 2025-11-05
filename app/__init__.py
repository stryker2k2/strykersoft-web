from flask import Flask, Blueprint, session
from app.main import main
from app.extensions import celery_init_app
import logging, uuid, os, sys
from datetime import datetime


logging.basicConfig(level=logging.INFO, stream=sys.stderr, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()
    # app.config['SESSION_COOKIE_SECURE'] = True
    app.config["DEBUG"] = True
    app.config["START_TIME"] = datetime.now()
    app.config["CELERY"] = {"broker_url": "redis://localhost:6379", "result_backend": "redis://localhost:6379"}
    app.config["SECRET_KEY"] = "CaptureTheFlag"

    celery_init_app(app)

    app.register_blueprint(main)

    return app
