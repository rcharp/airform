import click
import random
import inspect
import pkgutil

from sqlalchemy_utils import database_exists, create_database

from app.app import create_app
from app.extensions import db
from app.blueprints.user.models import User
from app.blueprints.api.models.app_auths import AppAuthorization
from app.blueprints.api.models.bases import Base
from app.blueprints.api.models.tables import Table
from importlib import import_module
from app.blueprints.api.api_functions import print_traceback

# Create an app context for the database connection.
app = create_app()
db.app = app


@click.group()
def cli():
    """ Run PostgreSQL related tasks. """
    pass


@click.command()
@click.option('--with-testdb/--no-with-testdb', default=False,
              help='Create a test db too?')
def init(with_testdb):
    """
    Initialize the database.

    :param with_testdb: Create a test database
    :return: None
    """
    db.drop_all()

    db.create_all()

    if with_testdb:
        db_uri = '{0}_test'.format(app.config['SQLALCHEMY_DATABASE_URI'])

        if not database_exists(db_uri):
            create_database(db_uri)


@click.command()
def seed():
    """
    Seed the database with an initial user.

    :return: User instance
    """
    if User.find_by_identity(app.config['SEED_ADMIN_EMAIL']) is not None:
        return None

    params = {
        'role': 'admin',
        'email': app.config['SEED_ADMIN_EMAIL'],
        'password': app.config['SEED_ADMIN_PASSWORD']
    }

    member = {
        'role': 'member',
        'email': app.config['SEED_MEMBER_EMAIL'],
        'password': app.config['SEED_ADMIN_PASSWORD']
    }

    User(**member).save()

    return User(**params).save()


@click.command()
def seedauth():
    """
    Seed the database with a couple user auths.

    :return: Nothing
    """

    # Seed auths
    auths = app.config['SEED_AUTHS']

    for auth in auths:
        a = AppAuthorization()
        a.user_id = 1
        a.app_name = auth['app_name']
        a.account = auth['account']
        a.account_id = auth['account_id']
        a.access_token = auth['access_token']

        a.save()


@click.command()
def seedintegrations():
    """
    Seed the database with a couple integrations.

    :return: Nothing
    """

    # Seed auths
    # auths = app.config['SEED_AUTHS']


@click.command()
@click.option('--with-testdb/--no-with-testdb', default=False,
              help='Create a test db too?')
@click.pass_context
def reset(ctx, with_testdb):
    """
    Init and seed automatically.

    :param with_testdb: Create a test database
    :return: None
    """
    ctx.invoke(init, with_testdb=with_testdb)
    ctx.invoke(seed)
    # ctx.invoke(seedauth)

    return None


@click.command()
def backup():
    """
    Backup the db.
    :return: None
    """
    # from flask.alchemydumps import AlchemyDumps
    #
    # alchemydumps = AlchemyDumps(app, db)
    #
    # return alchemydumps.create()
    return None


cli.add_command(init)
cli.add_command(seed)
cli.add_command(seedauth)
cli.add_command(reset)