import hashlib


def get_hashed_app_name(app_name):
    return str(hashlib.sha1(app_name.encode('utf-8')).hexdigest())
