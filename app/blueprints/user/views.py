from flask import (
    Blueprint,
    redirect,
    request,
    flash,
    Markup,
    url_for,
    render_template,
    json,
    jsonify,
    session)
from flask_login import (
    login_required,
    login_user,
    current_user,
    logout_user)

import time
from lib.safe_next_url import safe_next_url
from app.blueprints.user.decorators import anonymous_required
from app.blueprints.user.models import User
from app.blueprints.user.forms import (
    LoginForm,
    BeginPasswordResetForm,
    PasswordResetForm,
    SignupForm,
    WelcomeForm,
    UpdateCredentials)

import re
import os
import pytz
import stripe
import datetime
from lib.airtable_wrapper.airtable.airtable import Airtable
from app.extensions import cache, csrf, timeout, db
from importlib import import_module
from sqlalchemy import or_, and_
from app.blueprints.api.api_functions import print_traceback

user = Blueprint('user', __name__, template_folder='templates')


# Login and Credentials -------------------------------------------------------------------
@user.route('/login', methods=['GET', 'POST'])
@anonymous_required()
# @cache.cached(timeout=timeout)
@csrf.exempt
def login():
    form = LoginForm(next=url_for('user.dashboard'))

    if form.validate_on_submit():

        u = User.find_by_identity(request.form.get('identity'))

        if u and u.authenticated(password=request.form.get('password')):
            # As you can see remember me is always enabled, this was a design
            # decision I made because more often than not users want this
            # enabled. This allows for a less complicated login form.
            #
            # If however you want them to be able to select whether or not they
            # should remain logged in then perform the following 3 steps:
            # 1) Replace 'True' below with: request.form.get('remember', False)
            # 2) Uncomment the 'remember' field in user/forms.py#LoginForm
            # 3) Add a checkbox to the login form with the id/name 'remember'
            if login_user(u, remember=True) and u.is_active():
                u.update_activity_tracking(request.remote_addr)

                # Set the days left in the trial
                if current_user.trial:
                    trial_days_left = 14 - (datetime.datetime.now() - current_user.created_on.replace(tzinfo=None)).days
                    if trial_days_left < 0:
                        current_user.trial = False
                        current_user.save()

                next_url = request.form.get('next')

                if next_url:
                    return redirect(safe_next_url(next_url))

                if current_user.role == 'admin':
                    return redirect(url_for('admin.dashboard'))
            else:
                flash('This account has been disabled.', 'error')
        else:
            flash('Your username/email or password is incorrect.', 'error')

    else:
        print(form.errors)

    return render_template('user/login.html', form=form)


@user.route('/logout')
@login_required
# @cache.cached(timeout=timeout)
def logout():
    logout_user()

    flash('You have been logged out.', 'success')
    return redirect(url_for('user.login'))


@user.route('/account/begin_password_reset', methods=['GET', 'POST'])
@anonymous_required()
def begin_password_reset():
    form = BeginPasswordResetForm()

    if form.validate_on_submit():
        u = User.initialize_password_reset(request.form.get('identity'))

        flash('An email has been sent to {0}.'.format(u.email), 'success')
        return redirect(url_for('user.login'))

    return render_template('user/begin_password_reset.html', form=form)


@user.route('/account/password_reset', methods=['GET', 'POST'])
@anonymous_required()
def password_reset():
    form = PasswordResetForm(reset_token=request.args.get('reset_token'))

    if form.validate_on_submit():
        u = User.deserialize_token(request.form.get('reset_token'))

        if u is None:
            flash('Your reset token has expired or was tampered with.',
                  'error')
            return redirect(url_for('user.begin_password_reset'))

        form.populate_obj(u)
        u.password = User.encrypt_password(request.form.get('password'))
        u.save()

        if login_user(u):
            flash('Your password has been reset.', 'success')
            return redirect(url_for('user.dashboard'))

    return render_template('user/password_reset.html', form=form)


@user.route('/signup', methods=['GET', 'POST'])
@anonymous_required()
@csrf.exempt
# @cache.cached(timeout=timeout)
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        u = User()

        form.populate_obj(u)
        u.password = User.encrypt_password(request.form.get('password'))
        u.save()

        if login_user(u):

            from app.blueprints.user.tasks import send_welcome_email
            from app.blueprints.contact.mailerlite import create_subscriber

            send_welcome_email.delay(current_user.email)
            create_subscriber(current_user.email)

            flash("You've successfully signed up!", 'success')
                
            return redirect(url_for('user.dashboard'))

    return render_template('user/signup.html', form=form)


@user.route('/welcome', methods=['GET', 'POST'])
@login_required
def welcome():
    if current_user.username:
        flash('You already picked a username.', 'warning')
        return redirect(url_for('user.dashboard'))

    form = WelcomeForm()

    if form.validate_on_submit():
        current_user.username = request.form.get('username')
        current_user.save()

        flash('Your username has been set.', 'success')
        return redirect(url_for('user.dashboard'))

    return render_template('user/welcome.html', form=form, payment=current_user.payment_id)


@user.route('/settings/update_credentials', methods=['GET', 'POST'])
@login_required
def update_credentials():
    form = UpdateCredentials(current_user, uid=current_user.id)

    if form.validate_on_submit():
        new_password = request.form.get('password', '')
        current_user.email = request.form.get('email')

        if new_password:
            current_user.password = User.encrypt_password(new_password)

        current_user.save()

        flash('Your sign in settings have been updated.', 'success')
        return redirect(url_for('user.dashboard'))

    return render_template('user/update_credentials.html', form=form)


@user.route('/settings', methods=['GET', 'POST'])
@csrf.exempt
def settings():
    return redirect(url_for('user.dashboard'))


# Dashboard -------------------------------------------------------------------
@user.route('/dashboard', methods=['GET','POST'])
@login_required
@csrf.exempt
def dashboard():

    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))

    # Get settings trial information
    trial_days_left = -1
    if not current_user.subscription and not current_user.trial and current_user.role == 'member':
        flash(Markup("Your free trial has expired. Please <a href='/subscription/update'>sign up</a> for a plan to continue."), category='error')

    if current_user.trial and current_user.role == 'member':
        trial_days_left = 14 - (datetime.datetime.now() - current_user.created_on.replace(tzinfo=None)).days

    if trial_days_left < 0:
        current_user.trial = False
        current_user.save()

    return render_template('user/dashboard.html', current_user=current_user, trial_days_left=trial_days_left)


# Contact us -------------------------------------------------------------------
@user.route('/contact', methods=['GET','POST'])
@csrf.exempt
def contact():
    if request.method == 'POST':
        from app.blueprints.user.tasks import send_contact_us_email
        send_contact_us_email.delay(request.form['email'], request.form['message'])

        flash('Thanks for your email! You can expect a response shortly.', 'success')
        return redirect(url_for('user.dashboard'))
    return render_template('user/contact.html', current_user=current_user)


@user.route('/auth/<app>')
@login_required
@csrf.exempt
def auth(app):
    try:
        module = import_module("app.blueprints.api.apps." + app + '.' + app)
        account = module.account()

        flash("Successfully connected to your account.", 'success')
        return render_template('user/auth.html', app=app, account=account)
    except Exception as e:
        print_traceback(e)
        flash("There was an error connecting to this app. Please try again.", 'error')
        return redirect(url_for('user.dashboard'))


@user.route('/get_airtable_event_class', methods=['POST'])
@csrf.exempt
def get_airtable_event_class():
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
                                except Exception:
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


@user.route('/update_send_failure_email', methods=['POST'])
@csrf.exempt
def update_send_failure_email():
    if request.method == 'POST':
        try:
            if 'checked' in request.form:
                if request.form['checked'] == 'true':
                    current_user.send_failure_email = True
                else:
                    current_user.send_failure_email = False

                current_user.save()
                return jsonify({'success': {}})

        except Exception as e:
            print_traceback(e)
    return None


@user.route('/run_tests', methods=['GET','POST'])
@login_required
@csrf.exempt
def run_tests():

    try:
        from app.blueprints.api.api_tests import run_tests as run
        run()
    except Exception as e:
        print_traceback(e)
        pass

    return redirect(url_for('user.dashboard'))