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
  SECURE_TOKEN_COOKIES = False
  JWT_SECRET = os.environ.get('SECRET_KEY') or 'my-secret-never-guess'
  JWT_ALGORITHM = "HS256"
  ACCESS_COOKIE_NAME = "actk"
  REFRESH_COOKIE_NAME = "rftk"
  REFRESH_TOKEN_DURATION = timedelta(days=30)
  REFRESH_COOKIE_EXPIRATION = timedelta(days=31)
  CSRF_COOKIE_NAME = "x-csrf-token"
  MAIL_SERVER = os.environ.get('MAIL_SERVER')
  MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
  MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
  MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
  MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
  ADMINS = ['alvie97m@gmail.com']
  COLLEGES_PER_PAGE = 5
  SCHOLARSHIPS_PER_PAGE = 5
  PER_PAGE = 5
  UPLOADED_PHOTOS_DEST = 'static/photos/'
  UPLOADED_PHOTOS_URL = 'http://localhost:5000/api/file/photos/'
