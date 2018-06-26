import jwt
import os
import base64
from datetime           import datetime, timedelta
from hashlib            import md5
from time               import time
from flask              import current_app, url_for
from werkzeug.security  import generate_password_hash, check_password_hash
from app                import db

class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                **kwargs) if resources.has_prev else None
            }
        }

        return data



class User(PaginatedAPIMixin, db.Model):
    id                  = db.Column(db.Integer, primary_key=True)
    username            = db.Column(db.String(64), index=True, unique=True)
    email               = db.Column(db.String(120), index=True, unique=True)
    password_hash       = db.Column(db.String(128))
    last_seen           = db.Column(db.DateTime, default=datetime.utcnow)
    avatar              = db.Column(db.Text, nullable=True)
    token               = db.Column(db.String(32), index=True, unique=True)
    token_expiration    = db.Column(db.DateTime)

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
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'last_seen': self.last_seen.isoformat() + 'Z',
            '_links': {
                'self': url_for('api.get_user', id=self.id),
                'avatar': self.get_avatar(128) if self.avatar is None else self.avatar
            }
        }
        return data

    def from_dict(self, data):
        for field in ['username', 'email']:
            if field in data:
                setattr(self, field, data[field])

    #token functions

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token

        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

class College(db.Model):
    id                      = db.Column(db.Integer, primary_key=True)
    name                    = db.Column(db.String(256), index=True)
    room_and_board          = db.Column(db.Float(precision=2), default=0)
    created_at              = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at              = db.Column(db.DateTime, default=datetime.utcnow)
    type_of_institution     = db.Column(db.String(256), index=True)
    phone                   = db.Column(db.String(256), index=True)
    website                 = db.Column(db.Text, nullable=True)
    in_state_tuition        = db.Column(db.Float(precision=2), default=0)
    out_of_state_tuition    = db.Column(db.Float(precision=2), default=0)
    location                = db.Column(db.String(256), index=True)
    in_state_requirement    = db.Column(db.Text, nullable=True)
    counties                = db.Column(db.Text, nullable=True)
    religious_affiliation   = db.Column(db.String(256), index=True)
    setting                 = db.Column(db.String(256), index=True)
    number_of_students      = db.Column(db.Integer, default=0)
    #ranking                 = db.Column(db.Decimal(precision=5, scale=2), default=0)
    unweighted_hs_gpa       = db.Column(db.Numeric(precision=4, scale=2), default=0)
    sat                     = db.Column(db.Integer, default=0)
    act                     = db.Column(db.Integer, default=0)
    majors                  = db.Column(db.Text, nullable=True)
    campus_photo            = db.Column(db.Text, nullable=True)
    logo                    = db.Column(db.Text, nullable=True)
    hits                    = db.Column(db.BigInteger, default=0)
    total_ofs               = db.Column(db.Float(precision=2), default=0)
    total_is                = db.Column(db.Float(precision=2), default=0)

    def __repr__(self):
        return '<College {}>'.format(self.body)

    def calc_total_ofs(self):
        self.total_ofs = self.room_and_board + self.out_of_state_tuition

    def calc_total_is(self):
        self.total_is = self.room_and_board + self.in_state_tuition
