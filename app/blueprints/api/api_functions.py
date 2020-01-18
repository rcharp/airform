import re
import sys
import time
import pytz
import string
import random
import requests
import traceback
from datetime import datetime
from collections import defaultdict
from app.extensions import db
from sqlalchemy import exists, and_, or_, inspect
from flask import current_app
from importlib import import_module


# Create a distinct integration id for the integration.
def generate_id(size=8, chars=string.digits):

    # Generate a random 8-character user id
    new_id = int(''.join(random.choice(chars) for _ in range(size)))

    from app.blueprints.api.models.user_integrations import UserIntegration

    # Check to make sure there isn't already that id in the database
    if not db.session.query(exists().where(UserIntegration.id == new_id)).scalar():
        return integration_id
    else:
        generate_integration_id()


# Create a distinct auth id for the auth.
def generate_auth_id(size=6, chars=string.digits):

    # Generate a random 8-character user id
    auth_id = int(''.join(random.choice(chars) for _ in range(size)))

    from app.blueprints.api.models.app_auths import AppAuthorization

    # Check to make sure there isn't already that id in the database
    if not db.session.query(exists().where(AppAuthorization.id == auth_id)).scalar():
        return auth_id
    else:
        generate_auth_id()


# Create a distinct integration id for the integration.
def generate_app_id(size=6, chars=string.digits):

    # Generate a random 8-character user id
    app_id = int(''.join(random.choice(chars) for _ in range(size)))

    from app.blueprints.api.models.apps import App

    # Check to make sure there isn't already that id in the database
    if not db.session.query(exists().where(App.id == app_id)).scalar():
        return app_id
    else:
        generate_app_id()


def strip_imported_value(value):
    val = value.split(': ')[1].strip().split(';;')[0]
    return val


def print_traceback(e):
    traceback.print_tb(e.__traceback__)
    print(e)


def create_api_key_auth(current_user, api_key, app):
    try:
        from app.blueprints.api.models.app_auths import AppAuthorization

        if db.session.query(db.exists().where(and_(AppAuthorization.access_token == api_key, AppAuthorization.app_name == app))).scalar():
            flash("This account is already in use. Please try again.", 'error')
            return False
        else:
            from app.blueprints.api.models.apps import App

            a = AppAuthorization()

            a.id = generate_auth_id()
            a.app_id = App.query.with_entities(App.id).filter(App.name == app)
            a.app_name = app
            a.app_fullname = app.replace('_', ' ').title()
            a.access_token = api_key
            a.refresh_token = None
            a.user_id = current_user.id
            a.account_id = current_user.email
            a.account = 'XXXXXXXXXXXXXXXXX' + api_key[-3:]
            a.save()

            return True
    except Exception:
        return False