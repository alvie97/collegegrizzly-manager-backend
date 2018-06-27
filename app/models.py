import jwt
import os
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
            'username': self.username,
            'email': self.email,
            'last_seen': self.last_seen.isoformat() + 'Z',
            'avatar': self.get_avatar(128) if self.avatar is None else self.avatar
        }
        return data

    def from_dict(self, data):
        for field in ['username', 'email']:
            if field in data:
                setattr(self, field, data[field])


class College(db.Model):
    id                      = db.Column(db.Integer, primary_key=True)
    public_id               = db.Column(db.String(50), unique=True)
    name                    = db.Column(db.String(256))
    room_and_board          = db.Column(db.Float(precision=2), default=0)
    created_at              = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at              = db.Column(db.DateTime, default=datetime.utcnow)
    type_of_institution     = db.Column(db.String(256), nullable=True)
    phone                   = db.Column(db.String(256), nullable=True)
    website                 = db.Column(db.Text, nullable=True)
    in_state_tuition        = db.Column(db.Float(precision=2), default=0)
    out_of_state_tuition    = db.Column(db.Float(precision=2), default=0)
    location                = db.Column(db.String(256), nullable=True)
    in_state_requirement    = db.Column(db.Text, nullable=True)
    counties                = db.Column(db.Text, nullable=True)
    religious_affiliation   = db.Column(db.String(256), nullable=True)
    setting                 = db.Column(db.String(256), nullable=True)
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

    ATTR_FIELDS = [
        'public_id',
        'name',
        'room_and_board',
        'created_at',
        'updated_at',
        'type_of_institution',
        'phone',
        'website',
        'in_state_tuition',
        'out_of_state_tuition',
        'location',
        'in_state_requirement',
        'counties',
        'religious_affiliation',
        'setting',
        'number_of_students',
        'unweighted_hs_gpa',
        'sat',
        'act',
        'majors',
        'campus_photo',
        'logo',
        'hits',
        'total_ofs',
        'total_is'
    ]

    def __repr__(self):
        return '<College {}>'.format(self.name)

    def calc_total_ofs(self):
        self.total_ofs = self.room_and_board + self.out_of_state_tuition

    def calc_total_is(self):
        self.total_is = self.room_and_board + self.in_state_tuition

    def to_dict(self):
        return {
            'public_id': self.public_id,
            'name': self.name,
            'room_and_board': self.room_and_board,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'type_of_institution': self.type_of_institution,
            'phone': self.phone,
            'website': self.website,
            'in_state_tuition': self.in_state_tuition,
            'out_of_state_tuition': self.out_of_state_tuition,
            'location': self.location,
            'in_state_requirement': self.in_state_requirement,
            'counties': self.counties,
            'religious_affiliation': self.religious_affiliation,
            'setting': self.setting,
            'number_of_students': self.number_of_students,
            'unweighted_hs_gpa': self.unweighted_hs_gpa,
            'sat': self.sat,
            'act': self.act,
            'majors': self.majors,
            'campus_photo': self.campus_photo,
            'logo': self.logo,
            'hits': self.hits,
            'total_ofs': self.total_ofs,
            'total_is': self.total_is,
        }

    def from_dict(self, data):
        for field in self.ATTR_FIELDS:
            if field in data:
                setattr(self, field, data[field])
