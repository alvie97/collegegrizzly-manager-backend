import jwt
import os
from datetime import datetime, timedelta
from hashlib import md5
from time import time
from flask import current_app, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models.common import PaginatedAPIMixin


class User(PaginatedAPIMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(120), index=True, unique=True)
  password_hash = db.Column(db.String(128))
  last_seen = db.Column(db.DateTime, default=datetime.utcnow)
  avatar = db.Column(db.Text, nullable=True)

  def __repr__(self):
    return '<User {}>'.format(self.username)

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)

  def get_avatar(self, size):
    digest = md5(self.email.lower().encode('utf-8')).hexdigest()
    return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
        digest, size)

  def to_dict(self):
    data = {
        'email': self.email,
        'last_seen': self.last_seen.isoformat() + 'Z',
        'avatar': self.get_avatar(128) if self.avatar is None else self.avatar
    }
    return data

  def from_dict(self, data):
    for field in ['email']:
      if field in data:
        setattr(self, field, data[field])
