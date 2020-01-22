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
from airtable import Airtable


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


def get_airtable_bases(request):
    if request.method == 'POST':
        try:

            # Set this to true to include linked table records.
            # This will acts as a switch to quickly turn the functionality on and off.
            include_linked = False

            if 'base' in request.form and 'table' in request.form and 'token' in request.form:
                events = {}

                # Grab the base id, table, and api key from the form
                base_id = request.form['base']
                table_name = request.form['table']
                api_key = request.form['token']

                at = Airtable(base_id, table_name, api_key=api_key)

                # Get 20 records from the Airtable table and get their column names
                for page in at.get_iter(maxRecords=20):
                    for record in page:
                        events.update({'table_name': 'Table Name', 'record_id': 'Record Id'})
                        for field in record['fields']:
                            if include_linked and isinstance(record['fields'][field], list) and len(record['fields'][field]) > 0 and isinstance(record['fields'][field][0], str) and record['fields'][field][0].startswith('rec'):
                                try:
                                    linked_record = at.get(record['fields'][field][0])
                                    for linked_field in linked_record['fields']:
                                        if not (isinstance(linked_record['fields'][linked_field], list) and len(linked_record['fields'][linked_field]) > 0 and isinstance(linked_record['fields'][linked_field][0], str) and linked_record['fields'][linked_field][0].startswith('rec')):
                                            events.update({field + '::' + linked_field: field + '::' + linked_field})
                                except Exception as e:
                                    pass
                            else:
                                events.update({field: field})

                if not events:
                    from app.blueprints.api.apps.airtable.events import get_event_data_class
                    events = get_event_data_class(None)['airtable']

                return jsonify({'events': events})

        except Exception as e:
            print_traceback(e)
            return None


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