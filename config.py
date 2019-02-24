import os
from datetime import timedelta

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config(object):
    """Configuration class.

    Holds application configuration and environment variables.

    Attributes:
        SECRET_KEY: Application secret key for flask.
        SQLALCHEMY_DATABASE_URI: Uri to connect to the database.
        SQLALCHEMY_TRACK_MODIFICATIONS: ?.
        SECURE_TOKEN_COOKIES: cookies secure flag
        JWT_SECRET: jwt secret key
        JWT_ALGORITHM: algorithm used for jwt tokens. 
        ACCESS_TOKEN_COOKIE_NAME: name given to access "access token cookie"
        ACCESS_TOKEN_DURATION: expiration time of access token
        REFRESH_TOKEN_COOKIE_NAME: name given to access "refresh token cookie"
        REFRESH_TOKEN_DURATION: expiration time of refresh token
        CSRF_COOKIE_NAME: csrf cookie name 
        CSRF_HEADER_NAME: csrf header name
        MAIL_SERVER: mail server 
        MAIL_PORT: mail port
        MAIL_USE_TLS: use mail tls
        MAIL_USERNAME: mail username
        MAIL_PASSWORD: mail password
        ADMINS: administrators email.
        COLLEGES_PER_PAGE: colleges per page for pagination.
        USERS_PER_PAGE: users per page for pagination.
        SCHOLARSHIPS_PER_PAGE: scholarships per page for pagination.
        SUBMISSIONS_PER_PAGE: submissions per page for pagination.
        LOCATIONS_PER_PAGE: locations (states, counties, places, 
            consolidated cities) per page for pagination.
        PER_PAGE: items per page for pagination.
        UPLOADED_PHOTOS_DEST: photos destination directory.
        UPLOADED_PHOTOS_URL: url to access photos.
    """
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL") or "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get(
        "SQLALCHEMY_TRACK_MODIFICATIONS") or False
    SECURE_TOKEN_COOKIES = os.environ.get("SECURE_TOKEN_COOKIES") or False
    JWT_SECRET = os.environ.get("JWT_SECRET") or "my-secret-never-guess"
    JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM") or "HS256"
    ACCESS_TOKEN_COOKIE_NAME = os.environ.get(
        "ACCESS_TOKEN_COOKIE_NAME") or "actk"
    ACCESS_TOKEN_DURATION = os.environ.get(
        "ACCESS_TOKEN_DURATION") or timedelta(seconds=60)
    REFRESH_TOKEN_COOKIE_NAME = os.environ.get(
        "REFRESH_TOKEN_COOKIE_NAME") or "rftk"
    REFRESH_TOKEN_DURATION = os.environ.get(
        "REFRESH_TOKEN_DURATION") or timedelta(days=30)
    CSRF_COOKIE_NAME = os.environ.get("CSRF_COOKIE_NAME") or "X-CSRF-TOKEN"
    CSRF_HEADER_NAME = os.environ.get("CSRF_HEADER_NAME") or "X-XSRF-TOKEN"
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    ADMINS = os.environ.get("ADMINS") or ["alvie97m@gmail.com"]
    COLLEGES_PER_PAGE = os.environ.get("COLLEGES_PER_PAGE") or 5
    USERS_PER_PAGE = os.environ.get("USERS_PER_PAGE") or 5
    SCHOLARSHIPS_PER_PAGE = os.environ.get("SCHOLARSHIPS_PER_PAGE") or 5
    SUBMISSIONS_PER_PAGE = os.environ.get("SUBMISSIONS_PER_PAGE") or 5
    LOCATIONS_PER_PAGE = os.environ.get("LOCATIONS_PER_PAGE") or 5
    PER_PAGE = os.environ.get("PER_PAGE") or 5
    UPLOADED_PHOTOS_DEST = os.environ.get(
        "UPLOADED_PHOTOS_DEST") or "static/photos/"
    UPLOADED_PHOTOS_URL = os.environ.get(
        "UPLOADED_PHOTOS_URL") or "http://localhost:5000/api/files/photos/"
