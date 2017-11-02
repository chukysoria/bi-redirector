import time
from datetime import datetime
from functools import wraps

from cryptography.fernet import Fernet, InvalidToken

from biredirect import DB, SECRET_KEY

PROF_DATA = {}


def profile(fn):
    @wraps(fn)
    def with_profiling(*args, **kwargs):
        start_time = time.time()

        ret = fn(*args, **kwargs)

        elapsed_time = time.time() - start_time

        if fn.__name__ not in PROF_DATA:
            PROF_DATA[fn.__name__] = [0, []]
        PROF_DATA[fn.__name__][0] += 1
        PROF_DATA[fn.__name__][1].append(elapsed_time)

        return ret

    return with_profiling


def print_prof_data():
    msg = ''
    for fname, data in PROF_DATA.items():
        max_time = max(data[1])
        msg += f"\nFunction {fname} executed in {max_time:0.2f} seconds"
    return msg


def parse_date(str_date):
    if isinstance(str_date, str):
        return datetime.strptime(str_date, '%d/%m/%Y')
    elif isinstance(str_date, datetime):
        return str_date
    else:
        raise Exception


def get_config(name):
    value = DB.get_config_value(name.upper())
    if value:
        return value
    raise Exception(f"Config {name} doesn't exist")


def get_secure_config(name):
    token = get_config(name)
    try:
        return decrypt(token)
    except InvalidToken:
        raise Exception(f"Config {name} is not secured")


def encrypt(text):
    secret = SECRET_KEY.encode('UTF-8')
    fernet = Fernet(secret)
    token = fernet.encrypt(text.encode('UTF-8'))
    return token.decode('UTF-8')


def decrypt(token):
    try:
        secret = SECRET_KEY.encode('UTF-8')
        fernet = Fernet(secret)
        text = fernet.decrypt(token.encode('UTF-8'))
        return text.decode('UTF-8')
    except InvalidToken:
        return token
