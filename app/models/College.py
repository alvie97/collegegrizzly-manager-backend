from flask                  import url_for
from datetime               import datetime
from app                    import db, photos
from app.models.common      import PaginatedAPIMixin
from app.models.Scholarship import Scholarship
from app.models.Picture     import Picture
from hashlib                import md5

class College(PaginatedAPIMixin, db.Model):
    id                      = db.Column(db.Integer, primary_key=True)
    public_id               = db.Column(db.String(50), unique=True)
    name                    = db.Column(db.String(256))
    room_and_board          = db.Column(db.Numeric(8, 2), default=0)
    created_at              = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at              = db.Column(db.DateTime, default=datetime.utcnow)
    type_of_institution     = db.Column(db.String(256), nullable=True)
    phone                   = db.Column(db.String(256), nullable=True)
    website                 = db.Column(db.Text, nullable=True)
    in_state_tuition        = db.Column(db.Numeric(8, 2), default=0)
    out_of_state_tuition    = db.Column(db.Numeric(8, 2), default=0)
    location                = db.Column(db.String(256), nullable=True)
    in_state_requirement    = db.Column(db.Text, nullable=True)
    counties                = db.Column(db.Text, nullable=True)
    religious_affiliation   = db.Column(db.String(256), nullable=True)
    setting                 = db.Column(db.String(256), nullable=True)
    number_of_students      = db.Column(db.Integer, default=0)
    #ranking                 = db.Column(db.Decimal(precision=5, scale=2), default=0)
    unweighted_hs_gpa       = db.Column(db.Numeric(4, 2), default=0)
    sat                     = db.Column(db.Integer, default=0)
    act                     = db.Column(db.Integer, default=0)
    majors                  = db.Column(db.Text, nullable=True)
    hits                    = db.Column(db.BigInteger, default=0)
    Scholarships            = db.relationship('Scholarship',
                                              backref='college',
                                              cascade='all, delete-orphan',
                                              lazy='dynamic')

    Pictures                = db.relationship('Picture',
                                              backref='college',
                                              cascade='all, delete-orphan',
                                              lazy='dynamic')


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
        'majors'
    ]

    def get_avatar(self, size):
        digest = md5('test@email.com'.encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def __repr__(self):
        return '<College {}>'.format(self.name)

    def total_ofs(self):
        self.total_ofs = self.room_and_board + self.out_of_state_tuition

    def total_is(self):
        self.total_is = self.room_and_board + self.in_state_tuition

    def get_logo(self):
        logo = self.Pictures.filter_by(type='logo').first()

        if logo == None:
            return self.get_avatar(128)

        return photos.url(logo.name)

    def delete(self):
        """
        Scholarships doesn't need to be removed manually
        because, the cascade option takes care of it
        """
        pics = self.Pictures.all()

        for pic in pics:
            pic.delete()

        db.session.delete(self)

    def to_dict(self):
        return {
            'public_id': self.public_id,
            'name': self.name,
            'room_and_board': str(self.room_and_board),
            'created_at': self.created_at.isoformat() + 'Z',
            'updated_at': self.updated_at.isoformat() + 'Z',
            'type_of_institution': self.type_of_institution,
            'phone': self.phone,
            'website': self.website,
            'in_state_tuition': str(self.in_state_tuition),
            'out_of_state_tuition': str(self.out_of_state_tuition),
            'location': self.location,
            'in_state_requirement': self.in_state_requirement,
            'counties': self.counties,
            'religious_affiliation': self.religious_affiliation,
            'setting': self.setting,
            'number_of_students': self.number_of_students,
            'unweighted_hs_gpa': str(self.unweighted_hs_gpa),
            'sat': self.sat,
            'act': self.act,
            'majors': self.majors,
            'logo': self.get_logo(),
            'hits': self.hits,
            '_links': {
                'scholarships': url_for('scholarships',
                                        college_id=self.public_id),
                'pictures': url_for('pictures',
                                        college_id=self.public_id)
            }
        }

    def from_dict(self, data):
        for field in self.ATTR_FIELDS:
            if field in data:
                setattr(self, field, data[field])
        self.updated_at = datetime.utcnow()
