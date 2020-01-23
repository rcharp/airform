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


# noinspection PyInterpreter
# def get_table(table_name, base_id, api_key):
#     # noinspection PyInterpreter
#     try:
#
#         # Set this to true to include linked table records.
#         # This will acts as a switch to quickly turn the functionality on and off.
#         include_linked = False
#
#         at = Airtable(base_id, table_name, api_key=api_key)
#
#         columns = dict()
#
#         # Get 20 records from the Airtable table and get their column names
#         for page in at.get_iter(maxRecords=5):
#             return page
#             for record in page:
#                 for field in record['fields']:
#                     print(field)
#                     # if include_linked and isinstance(record['fields'][field], list) and len(
#                     #         record['fields'][field]) > 0 and isinstance(record['fields'][field][0], str) and \
#                     #         record['fields'][field][0].startswith('rec'):
#                     #     try:
#                     #         linked_record = at.get(record['fields'][field][0])
#                     #         for linked_field in linked_record['fields']:
#                     #             if not (isinstance(linked_record['fields'][linked_field], list) and len(
#                     #                     linked_record['fields'][linked_field]) > 0 and isinstance(
#                     #                     linked_record['fields'][linked_field][0], str) and
#                     #                     linked_record['fields'][linked_field][0].startswith('rec')):
#                     #                 return
#                     #                 # events.update({field + '::' + linked_field: field + '::' + linked_field})
#                     #     except Exception as e:
#                     #         pass
#                     # else:
#                     #     columns.update({field: field})
#
#     except Exception as e:
#         print_traceback(e)
#         return None

def get_table(table_name, base_id, api_key):
    try:
        # Set this to true to include linked table records.
        # This will acts as a switch to quickly turn the functionality on and off.
        include_linked = False

        at = Airtable(base_id, table_name, api_key=api_key)

        table = list()
        columns = list()

        # Get 20 records from the Airtable table and get their column names
        for page in at.get_iter(maxRecords=100):

            for record in page:
                r = dict()
                for field in record['fields']:
                    if field not in columns:
                        columns.append(field)
                    # if include_linked and isinstance(record['fields'][field], list) and len(
                    #         record['fields'][field]) > 0 and isinstance(record['fields'][field][0], str) and \
                    #         record['fields'][field][0].startswith('rec'):
                    #     try:
                    #         linked_record = at.get(record['fields'][field][0])
                    #         for linked_field in linked_record['fields']:
                    #             if not (isinstance(linked_record['fields'][linked_field], list) and len(
                    #                     linked_record['fields'][linked_field]) > 0 and isinstance(
                    #                     linked_record['fields'][linked_field][0], str) and
                    #                     linked_record['fields'][linked_field][0].startswith('rec')):
                    #
                    #                 records = dict()
                    #                 records.update({field + '::' + linked_field: field + '::' + linked_field})
                    #                 table.append(r)
                    #     except Exception as e:
                    #         pass
                    # else:

                    r.update({field: record['fields'][field]})
                table.append(r)

        # Sort the columns alphabetically
        columns.sort()

        return table, columns
    except Exception as e:
        return None


def delete_table(table_id):
    from app.blueprints.api.tasks import delete_table
    delete_table(table_id)


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