import logging
import os
from logging.handlers import SMTPHandler

import stripe

from werkzeug.contrib.fixers import ProxyFix
from flask import Flask, render_template
from celery import Celery
from itsdangerous import URLSafeTimedSerializer
from flask_compress import Compress

from app.blueprints.admin import admin
from app.blueprints.page import page
from app.blueprints.contact import contact
from app.blueprints.user import user
from app.blueprints.api import api
from app.blueprints.billing import billing
from app.blueprints.user.models import User
from app.blueprints.page.date import get_string_from_datetime, get_datetime_from_string, get_dt_string
from app.blueprints.api.models.app_auths import AppAuthorization
from app.blueprints.billing.template_processors import (
  format_currency,
  current_year
)
from app.extensions import (
    debug_toolbar,
    mail,
    csrf,
    db,
    login_manager,
    cache
)

CELERY_TASK_LIST = [
    'app.blueprints.api.tasks',
    'app.blueprints.contact.tasks',
    'app.blueprints.user.tasks',
    'app.blueprints.billing.tasks'
]

CELERY_WEBHOOK_LIST = [
    'app.blueprints.billing.webhooks',
    'app.blueprints.api.apps.airtable.webhook'
]

'''
Uncomment his code in order to create a Celery worker for each app that
uses manual webhooks. For future development.
'''
# for app in get_webhook_apps():
#     CELERY_TASK_LIST.append('app.blueprints.api.apps.' + app + '.webhook')


def create_celery_app(app=None):
    """
    Create a new Celery object and tie together the Celery config to the app's
    config. Wrap all tasks in the context of the application.

    :param app: Flask app
    :return: Celery app
    """
    app = app or create_app()
    celery = Celery(broker=app.config.get('CELERY_BROKER_URL'), include=CELERY_TASK_LIST)
    celery.conf.update(app.config)
    celery.conf.beat_schedule = {}
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_celery_webhook_app(app=None):
    """
    Create a new Celery object and tie together the Celery config to the app's
    config. Wrap all tasks in the context of the application.

    :param app: Flask app
    :return: Celery app
    """
    app = app or create_app()
    celery = Celery(broker=app.config.get('CLOUDAMQP_URL'), include=CELERY_WEBHOOK_LIST)
    celery.conf.update(app.config)
    celery.conf.beat_schedule = app.config.get('CELERYBEAT_SCHEDULE')

    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_app(settings_override=None):
    """
    Create a Flask application using the app factory pattern.

    :param settings_override: Override settings
    :return: Flask app
    """
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object('config.settings')
    app.config.from_pyfile('settings.py', silent=True)

    if settings_override:
        app.config.update(settings_override)

    stripe.api_key = app.config.get('STRIPE_SECRET_KEY')
    stripe.api_version = '2018-02-28'

    middleware(app)
    error_templates(app)
    exception_handler(app)
    app.register_blueprint(admin)
    app.register_blueprint(page)
    app.register_blueprint(contact)
    app.register_blueprint(user)
    app.register_blueprint(api)
    app.register_blueprint(billing)
    template_processors(app)
    extensions(app)
    authentication(app, User)

    # Compress Flask app
    COMPRESS_MIMETYPES = ['text/html' 'text/css', 'application/json']
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500
    Compress(app)

    return app


def extensions(app):
    """
    Register 0 or more extensions (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    debug_toolbar.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app, config={'CACHE_TYPE': 'redis'})

    return None


def template_processors(app):
    """
    Register 0 or more custom template processors (mutates the app passed in).

    :param app: Flask application instance
    :return: App jinja environment
    """
    app.jinja_env.filters['format_currency'] = format_currency
    app.jinja_env.filters['pretty_date_filter'] = pretty_date_filter
    app.jinja_env.filters['logo_filter'] = logo_filter
    app.jinja_env.globals.update(current_year=current_year)

    return app.jinja_env


def authentication(app, user_model):
    """
    Initialize the Flask-Login extension (mutates the app passed in).

    :param app: Flask application instance
    :param user_model: Model that contains the authentication information
    :type user_model: SQLAlchemy model
    :return: None
    """
    login_manager.login_view = 'user.login'

    @login_manager.user_loader
    def load_user(uid):
        return user_model.query.get(uid)

    #@login_manager.token_loader
    def load_token(token):
        duration = app.config['REMEMBER_COOKIE_DURATION'].total_seconds()
        max = 999999999999
        serializer = URLSafeTimedSerializer(app.secret_key)

        data = serializer.loads(token, max_age=max)
        user_uid = data[0]

        return user_model.query.get(user_uid)


def middleware(app):
    """
    Register 0 or more middleware (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    # Swap request.remote_addr with the real IP address even if behind a proxy.
    app.wsgi_app = ProxyFix(app.wsgi_app)

    return None


def error_templates(app):
    """
    Register 0 or more custom error pages (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """

    def render_status(status):
        """
         Render a custom template for a specific status.
           Source: http://stackoverflow.com/a/30108946

         :param status: Status as a written name
         :type status: str
         :return: None
         """
        # Get the status code from the status, default to a 500 so that we
        # catch all types of errors and treat them as a 500.
        code = getattr(status, 'code', 500)
        return render_template('errors/{0}.html'.format(code)), code

    for error in [404, 500]:
        app.errorhandler(error)(render_status)

    return None


def exception_handler(app):
    """
    Register 0 or more exception handlers (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    mail_handler = SMTPHandler((app.config.get('MAIL_SERVER'),
                                app.config.get('MAIL_PORT')),
                               app.config.get('MAIL_USERNAME'),
                               [app.config.get('MAIL_USERNAME')],
                               '[Exception handler] A 5xx was thrown',
                               (app.config.get('MAIL_USERNAME'),
                                app.config.get('MAIL_PASSWORD')),
                               secure=())

    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(logging.Formatter("""
    Time:               %(asctime)s
    Message type:       %(levelname)s


    Message:

    %(message)s
    """))
    app.logger.addHandler(mail_handler)

    return None


def logo_filter(arg, k):
    if 'Imported from ' in arg:
        return 'import'
    return k


def pretty_date_filter(arg):
    time_string = str(arg)
    dt = get_datetime_from_string(time_string)

    return get_dt_string(dt)
