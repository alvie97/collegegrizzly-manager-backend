import os
import datetime
import dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
dotenv.load_dotenv(os.path.join(basedir, ".env"))


class Config(object):
    """Configuration class.

    Holds application configuration and environment variables.

    Attributes:
        SECRET_KEY: Application secret key for flask.
        SQLALCHEMY_DATABASE_URI: Uri to connect to the database.
        SQLALCHEMY_TRACK_MODIFICATIONS: ?.
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

    # JWT
    JWT_TOKEN_LOCATION = os.environ.get("JWT_TOKEN_LOCATION") or ['cookies']
    JWT_BLACKLIST_ENABLED = os.environ.get("JWT_BLACKLIST_ENABLED") or True
    JWT_BLACKLIST_TOKEN_CHECKS = os.environ.get(
        "JWT_BLACKLIST_TOKEN_CHECKS") or ['refresh']
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET") or "my-secret-never-guess"
    JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM") or "HS256"
    JWT_COOKIE_SECURE = os.environ.get("JWT_COOKIE_SECURE") or False
    JWT_COOKIE_CSRF_PROTECT = os.environ.get(
        "JWT_COOKIE_CSRF_PROTECT") or False
    JWT_ACCESS_COOKIE_PATH = os.environ.get(
        "JWT_ACCESS_COOKIE_PATH") or "/api/"
    JWT_REFRESH_COOKIE_PATH = os.environ.get(
        "JWT_REFRESH_COOKIE_PATH") or "/auth/token/refresh"
    JWT_ACCESS_COOKIE_NAME = os.environ.get(
        "ACCESS_TOKEN_COOKIE_NAME") or "actk"
    JWT_REFRESH_COOKIE_NAME = os.environ.get(
        "REFRESH_TOKEN_COOKIE_NAME") or "rftk"
    JWT_ACCESS_TOKEN_EXPIRES = os.environ.get(
        "JWT_ACCESS_TOKEN_EXPIRES") or datetime.timedelta(minutes=5)
    JWT_REFRESH_TOKEN_EXPIRES = os.environ.get(
        "JWT_ACCESS_TOKEN_EXPIRES") or datetime.timedelta(days=7)
    JWT_SESSION_COOKIE = os.environ.get("JWT_SESSION_COOKIE") or True
    # endJWT

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
