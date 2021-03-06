# import dateutil.relativedelta
# import dateutil.parser
from datetime import tzinfo, timezone, timedelta, datetime as dtime
import datetime
import time
import pytz
import tzlocal
# import app.blueprints.simple.prettydate as p
from json import dumps

now = dtime.now()
yesterday = now - datetime.timedelta(days=1)
three_days_ago = now - datetime.timedelta(days=3)
one_week_ago = now - datetime.timedelta(days=7)
one_month_ago = now - datetime.timedelta(days=30)
six_weeks_ago = now - datetime.timedelta(days=45)
two_months_ago = now - datetime.timedelta(days=60)
three_months_ago = now - datetime.timedelta(days=90)
six_months_ago = now - datetime.timedelta(days=180)
twelve_months_ago = now - datetime.timedelta(days=365)
twenty_four_months_ago = now - datetime.timedelta(days=730)

"""Get timestamp################################################################
def get_timestamp(timestamp):
    timestamp = timestamp.replace("T", " ")
    timestamp = timestamp.replace("Z", "")
    time_tuple = time.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    timestamp = int(time.mktime(time_tuple))
    return timestamp

def convert_start_time(int_time):
    #int_time = int_time.replace("/", "-")
    int_time = str(int_time) + " 00:00:00"
    time_tuple = datetime.strptime(int_time, "%m/%d/%Y %H:%M:%S")
    return time_tuple

def convert_end_time(int_time):
    #int_time = int_time.replace("/", "-")
    int_time = str(int_time) + " 23:59:59"
    time_tuple = datetime.strptime(int_time, "%m/%d/%Y %H:%M:%S")
    return time_tuple
"""


# Time conversions ###################################
def get_short_date_string(timestamp):
    dt = dtime.fromtimestamp(timestamp)
    dt=dt.replace(tzinfo=None)
    return dt.strftime("%B %d")


def get_formatted_date_string(timestamp):
    dt = dtime.fromtimestamp(timestamp)
    dt=dt.replace(tzinfo=None)
    return dt.strftime("%B %d, %Y")


def get_datetime_string(timestamp):
    dt = dtime.fromtimestamp(timestamp)
    dt=dt.replace(tzinfo=None)
    return dt.strftime("%B %d, %Y %H:%M:%S")


def get_dt_string(dt):
    return dt.strftime("%B %d, %Y %H:%M:%S")


def get_string_from_datetime(dt):
    tz = tzlocal.get_localzone()
    date = tz.localize(dt)
    return date.strftime('%Y-%m-%d %H:%M:%S.%f')


def get_string_from_utc_datetime(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S.%f')


def get_iso_string_from_utc_datetime(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%S') + '+00:00'


def get_shortened_iso_string_from_utc_datetime(dt):
    return dt.strftime('%Y-%m-%dT%H:%M')


def convert_timestamp_to_datetime_utc(timestamp):
    dt_naive_utc = dtime.utcfromtimestamp(timestamp)
    return dt_naive_utc.replace(tzinfo=pytz.utc)


def get_datetime(timestamp):
    dt = dtime.fromtimestamp(timestamp)
    dt=dt.replace(tzinfo=None)
    return dt


def get_datetime_from_string(time_string):
    time_string = str(time_string)
    time_string = time_string.replace('T', ' ').replace('Z', '').replace('+00:00', '')
    dt = dtime.strptime(time_string, '%Y-%m-%d %H:%M:%S.%f')
    return dt


def get_tsheets_datetime_from_string(time_string):
    time_string = str(time_string)
    dt = dtime.strptime(time_string, '%Y-%m-%dT%H:%M')
    return dt


def adjust_tsheets_datetime(time_string, direction, hours, minutes):
    dt = get_tsheets_datetime_from_string(time_string) + timedelta(hours=hours, minutes=minutes) if direction == 'forward' else get_tsheets_datetime_from_string(
        time_string) - timedelta(hours=hours, minutes=minutes) if direction == 'backward' else time_string

    dt = str(dt)
    dt = dt.replace(' ', 'T').replace(dt[-3:], '')
    return dt


def get_utc_datetime_from_string(time_string):
    time_string = str(time_string)
    time_string = time_string.replace('+00:00', '')
    dt = dtime.strptime(time_string, '%Y-%m-%dT%H:%M:%S')
    return dt.astimezone(pytz.UTC)


def convert_local_timestring_to_utc_string(time_string):
    time_string = str(time_string)
    offset = time_string[-6:]
    time_string = time_string.replace(time_string[-6:], '')
    direction = 'forward' if offset[0] == '-' else 'backward' if offset[0] == '+' else None

    if not direction:
        return

    hours = int(offset[1:3])
    minutes = int(offset[4:])

    dt = dtime.strptime(time_string, '%Y-%m-%dT%H:%M:%S')
    dt = dt + timedelta(hours=hours, minutes=minutes) if direction == 'forward' else dt - timedelta(hours=hours, minutes=minutes)
    return get_shortened_iso_string_from_utc_datetime(dt)


def get_local_timestring_offset(time_string):
    time_string = str(time_string)
    offset = time_string[-6:]
    return offset


def get_local_timestring_offset_parts(offset):
    if offset is None:
        return None, None, None

    direction = 'backward' if offset[0] == '-' else 'forward' if offset[0] == '+' else None

    if not direction:
        return None, None, None

    try:
        hours = int(offset[1:3])
        minutes = int(offset[4:])
    except Exception:
        hours = None
        minutes = None

    return direction, hours, minutes


def get_shortened_datetime_from_string(time_string):
    time_string = str(time_string)
    time_string = time_string.replace('T', ' ').replace('Z', '').replace('+00:00', '')
    dt = dtime.strptime(time_string, '%Y-%m-%d')
    return dt


def get_datetime_from_datestring(time_string):
    time_string = str(time_string)
    time_string = time_string.replace('T', ' ').replace('Z', '').replace('+00:00', '')
    dt = dtime.strptime(time_string, '%Y-%m-%d')
    return dt


# def pretty_date(timestamp):
#     dt = dtime.fromtimestamp(timestamp)
#     dt=dt.replace(tzinfo=None)
#     return p.date(dt)


def datetime_to_int(dt):
    return time.mktime(dt)


### Datetime JSON serializer###################################################
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")


def jsonify(datetime_obj):
    return dumps(datetime_obj, default=json_serial)

##DateTime formatting##########################################################
"""
def pretty_date(time=False):

    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    ""
    from datetime import datetime

    #time = time.replace(tzinfo=None)
    now = datetime.now()
    diff = now - datetime.today()

    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time
    elif not time:
        diff = now - now

    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "Just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "A minute ago"
        if second_diff < 3600:
            return str(second_diff / 60) + " minutes ago"
        if second_diff < 7200:
            return "An hour ago"
        if second_diff < 86400:
            return "About " + str(second_diff / 3600) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        if day_diff == 1:
            return str(day_diff) + " day ago"
        else:
            return str(day_diff) + " days ago"
    if day_diff < 31:
        if day_diff / 7 == 1:
            return "About a week ago"
        else:
            return str(day_diff / 7) + " weeks ago"
    if day_diff < 365:
        if day_diff / 30 == 1:
            return str(day_diff / 30) + " month ago"
        else:
            return str(day_diff / 30) + " months ago"
    if day_diff / 365 == 1:
        return "About a year ago"
    else:
        return str(day_diff / 365) + " years ago"
"""
