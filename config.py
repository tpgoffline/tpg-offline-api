import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-really-never-guess"
    JSONIFY_PRETTYPRINT_REGULAR = False
    DEBUG = True
