import os
basedir = os.path.abspath(os.path.dirname(__file__))
    
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-really-never-guess'
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://user:password@host:port/tpgoffline-apns_apns"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    DEBUG = True
