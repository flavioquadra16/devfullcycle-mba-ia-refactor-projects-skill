from datetime import datetime, timezone
import re

VALID_STATUSES = ['pending', 'in_progress', 'done', 'cancelled']
VALID_ROLES = ['user', 'admin', 'manager']
MAX_TITLE_LENGTH = 200
MIN_TITLE_LENGTH = 3
MIN_PASSWORD_LENGTH = 4
DEFAULT_PRIORITY = 3
DEFAULT_COLOR = '#000000'
REPORT_WINDOW_DAYS = 7


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def format_date(date_obj):
    if date_obj:
        return str(date_obj)
    return None


def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def validate_email(email):
    return bool(re.match(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$', email or ''))


def sanitize_string(value):
    if value:
        return value.strip()
    return value


def generate_id():
    import uuid
    return str(uuid.uuid4())


def log_action(action, details=None):
    timestamp = utc_now()
    print(f"[{timestamp}] ACTION: {action}")
    if details:
        print(f"  DETAILS: {details}")


def parse_date(date_string):
    try:
        return datetime.strptime(date_string, '%Y-%m-%d')
    except (TypeError, ValueError):
        return None


def is_valid_color(color):
    return bool(color) and len(color) == 7 and color[0] == '#'
