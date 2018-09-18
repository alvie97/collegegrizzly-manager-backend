import os
from dotenv import load_dotenv
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
  SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
  SQLALCHEMY_DATABASE_URI = os.environ.get(
      'DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  JWT_SECRET = os.environ.get('SECRET_KEY') or 'my-secret-never-guess'
  JWT_ALGORITHM = "HS256"
  ACCESS_COOKIE_NAME = "actk"
  REFFRESH_COOKIE_NAME = "rftk"
  CSRF_COOKIE_NAME = "x-csrf-token"
  ACCESS_TOKEN_DURATION = timedelta(seconds=60)
  REFRESH_TOKEN_DURATION = timedelta(days=7)
  MAIL_SERVER = os.environ.get('MAIL_SERVER')
  MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
  MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
  MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
  MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
  ADMINS = ['alvie97m@gmail.com']
  COLLEGES_PER_PAGE = 10
  SCHOLARSHIPS_PER_PAGE = 1
  UPLOADED_PHOTOS_DEST = 'static/photos/'
  UPLOADED_PHOTOS_URL = 'http://localhost:5000/api/file/photos/'
