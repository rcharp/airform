from datetime import timedelta
import os
from celery.schedules import crontab


DEBUG = True
LOG_LEVEL = 'DEBUG'  # CRITICAL / ERROR / WARNING / INFO / DEBUG

SECRET_KEY = os.environ.get('SECRET_KEY', None)
CRYPTO_KEY = os.environ.get('CRYPTO_KEY', None)
PASSWORD = os.environ.get('PASSWORD', None)

# Flask-Mail.
MAIL_USERNAME = os.environ.get('MAIL_USERNAME', None)
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', None)
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME', None)
MAIL_SERVER = os.environ.get('MAIL_SERVER', None)
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True

CARD_NAME = ''
CARD_NUMBER = ''
CARD_MONTH = ''
CARD_YEAR = ''
CARD_CVV = ''

# Cache
CACHE_TYPE = 'redis'
CACHE_REDIS_HOST = os.environ.get('CACHE_REDIS_HOST', None)
CACHE_REDIS_PASSWORD = os.environ.get('CACHE_REDIS_PASSWORD', None)
CACHE_DEFAULT_TIMEOUT = os.environ.get('CACHE_DEFAULT_TIMEOUT', None)
CACHE_REDIS_PORT = os.environ.get('CACHE_REDIS_PORT', None)
CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL', None)

# Celery Heartbeat.
BROKER_HEARTBEAT = 10
BROKER_HEARTBEAT_CHECKRATE = 2

# Celery.
CLOUDAMQP_URL = os.environ.get('CLOUDAMQP_URL', None)
REDIS_URL = os.environ.get('CACHE_REDIS_URL', None)
HEROKU_REDIS_COPPER_URL = os.environ.get('HEROKU_REDIS_COPPER_URL', None)
REDBEAT_REDIS_URL = os.environ.get('CACHE_REDIS_URL', None)

CELERY_BROKER_URL = os.environ.get('CACHE_REDIS_URL', None)
CELERY_BROKER_HEARTBEAT = 10
CELERY_BROKER_HEARTBEAT_CHECKRATE = 2
CELERY_RESULT_BACKEND = os.environ.get('CACHE_REDIS_URL', None)
CELERY_REDIS_URL = os.environ.get('CACHE_REDIS_URL', None)
CELERY_REDIS_HOST = os.environ.get('CACHE_REDIS_HOST', None)
CELERY_REDIS_PORT = os.environ.get('CACHE_REDIS_PORT', None)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_EXPIRES = 300
CELERY_REDIS_MAX_CONNECTIONS = 20
CELERY_TASK_FREQUENCY = 2  # How often (in minutes) to run this task
CELERYBEAT_SCHEDULE = {
    'mark-soon-to-expire-credit-cards': {
        'task': 'app.blueprints.billing.tasks.mark_old_credit_cards',
        'schedule': crontab(hour=0, minute=0)
    },
    'send_three_day_expiration_emails': {
        'task': 'app.blueprints.billing.tasks.send_three_day_expiration_emails',
        'schedule': crontab(hour=12, minute=0)
    },
    'send_trial_expired_emails': {
        'task': 'app.blueprints.billing.tasks.send_trial_expired_emails',
        'schedule': crontab(hour=12, minute=0)
    },
    'send_no_integrations_emails': {
        'task': 'app.blueprints.billing.tasks.send_no_integrations_emails',
        'schedule': crontab(hour=12, minute=0)
    }
}

'''
Uncomment this code in order to set a worker for each app that uses manual webhoooks.
If uncommenting this code, make sure to comment out the webhooks dict in the above
CELERYBEAT_SCHEDULE dictionary
'''
# webhook_apps = get_webhook_apps()
# for app in webhook_apps:
#     CELERYBEAT_SCHEDULE.update(
#         {
#             app: {
#                 'task': 'app.blueprints.api.apps.' + app + '.webhook.webhook',
#                 'schedule': crontab(minute='*/' + str(CELERY_TASK_FREQUENCY))
#             }
#         })

# SQLAlchemy.
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', None)
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_USER = os.environ.get('SQLALCHEMY_USER', None)
SQLALCHEMY_DATABASE = os.environ.get('SQLALCHEMY_DATABASE', None)
SQLALCHEMY_HOST = os.environ.get('SQLALCHEMY_HOST', None)
SQLALCHEMY_PASSWORD = os.environ.get('SQLALCHEMY_PASSWORD', None)

# User.
SEED_ADMIN_EMAIL = os.environ.get('SEED_ADMIN_EMAIL', None)
SEED_ADMIN_PASSWORD = os.environ.get('SEED_ADMIN_PASSWORD', None)
SEED_MEMBER_EMAIL = ''
REMEMBER_COOKIE_DURATION = timedelta(days=90)

# Mailgun.
MAILGUN_LOGIN = os.environ.get('MAILGUN_LOGIN', None)
MAILGUN_PASSWORD = os.environ.get('MAILGUN_PASSWORD', None)
MAILGUN_HOST = os.environ.get('MAILGUN_HOST', None)
MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN', None)
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY', None)

# Turn off debug intercepts
DEBUG_TB_INTERCEPT_REDIRECTS = False
DEBUG_TB_ENABLED = False

# Ngrok
SITE_URL = 'https://www.domain.com'

# Webhook
WEBHOOK_URL = 'https://www.domain.com/webhook'

# Mailerlite
MAILERLITE_API_KEY = os.environ.get('MAILERLITE_API_KEY', None)

# Google
GOOGLE_APPLICATION_CREDENTIALS=os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', None)
GOOGLE_PROJECT_ID=os.environ.get('GOOGLE_PROJECT_ID', None)
GOOGLE_CLIENT_ID=os.environ.get('GOOGLE_CLIENT_ID', None)
GOOGLE_CLIENT_SECRET=os.environ.get('GOOGLE_CLIENT_SECRET', None)
GOOGLE_TOKEN_URI=os.environ.get('GOOGLE_TOKEN_URI', None)
GOOGLE_AUTH_URI=os.environ.get('GOOGLE_AUTH_URI', None)
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.compose','https://www.googleapis.com/auth/gmail.modify','email']
GOOGLE_DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive','email']
GOOGLE_CONTACTS_SCOPES = ['https://www.googleapis.com/auth/contacts','email']
GOOGLE_SHEETS_SCOPES = ['https://www.googleapis.com/auth/spreadsheets','email']
GOOGLE_PUSH_ENDPOINT=os.environ.get('GOOGLE_PUSH_ENDPOINT', None)
GOOGLE_CALLBACK_URL=os.environ.get('GOOGLE_CALLBACK_URL', None)

# Slack
SLACK_CLIENT_ID=os.environ.get('SLACK_CLIENT_ID', None)
SLACK_CLIENT_SECRET=os.environ.get('SLACK_CLIENT_SECRET', None)
SLACK_SCOPE=os.environ.get('SLACK_SCOPE', None)
SLACK_AUTH_URL=os.environ.get('SLACK_AUTH_URL', None)
SLACK_BUTTON=os.environ.get('SLACK_BUTTON', None)

# Airtable
AIRTABLE_KEY = os.environ.get('AIRTABLE_KEY', None)
AIRTABLE_BASE = os.environ.get('AIRTBALE_BASE', None)
D_AIRTABLE_KEY = os.environ.get('D_AIRTABLE_KEY', None)
D_AIRTABLE_BASE = os.environ.get('D_AIRTBALE_BASE', None)

# Billing.
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', None)
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', None)
STRIPE_API_VERSION = '2018-02-28'
STRIPE_AUTHORIZATION_LINK = os.environ.get('STRIPE_CONNECT_AUTHORIZE_LINK', None)
STRIPE_PLANS = {
    '0': {
        'id': 'free',
        'name': 'Forever Free',
        'amount': 0000,
        'currency': 'usd',
        'interval': 'month',
        'interval_count': 1,
        'trial_period_days': 0,
        'statement_descriptor': 'FREE',
        'metadata': {}
    },
    '1': {
        'id': 'hobby',
        'name': 'Hobby',
        'amount': 700,
        'currency': 'usd',
        'interval': 'month',
        'interval_count': 1,
        'trial_period_days': 0,
        'statement_descriptor': 'HOBBY',
        'metadata': {}
    },
    '2': {
        'id': 'startup',
        'name': 'Startup',
        'amount': 2000,
        'currency': 'usd',
        'interval': 'month',
        'interval_count': 1,
        'trial_period_days': 0,
        'statement_descriptor': 'STARTUP',
        'metadata': {
            'recommended': True
        }
    },
    '3': {
        'id': 'professional',
        'name': 'Professional',
        'amount': 5000,
        'currency': 'usd',
        'interval': 'month',
        'interval_count': 1,
        'trial_period_days': 0,
        'statement_descriptor': 'PROFESSIONAL',
        'metadata': {}
    },
    '4': {
        'id': 'premium',
        'name': 'Premium',
        'amount': 12000,
        'currency': 'usd',
        'interval': 'month',
        'interval_count': 1,
        'trial_period_days': 0,
        'statement_descriptor': 'PREMIUM',
        'metadata': {}
    },
    '5': {
        'id': 'enterprise',
        'name': 'Enterprise',
        'amount': 25000,
        'currency': 'usd',
        'interval': 'month',
        'interval_count': 1,
        'trial_period_days': 0,
        'statement_descriptor': 'ENTERPRISE',
        'metadata': {}
    },
    '6': {
        'id': 'developer',
        'name': 'Developer',
        'amount': 1,
        'currency': 'usd',
        'interval': 'month',
        'interval_count': 1,
        'trial_period_days': 0,
        'statement_descriptor': 'DEVELOPER',
        'metadata': {}
    }
}

# APIs
API = {
    'gmail': {
    }
}
