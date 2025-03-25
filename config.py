import os 
from sqlalchemy import create_engine
import urllib

class Config(object):
    SECRET_KEY='Clave nueva'
    SESION_COOKIE_SECURE=False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:conejillo18@127.0.0.1/examenpizzas'
    SQLALCHEMY_TRACK_MODIFICATIONS = False