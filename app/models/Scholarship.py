from datetime           import datetime, timedelta
from time               import time
from flask              import current_app, url_for
from app                import db
from app.models.common  import PaginatedAPIMixin

class Scholarship(PaginatedAPIMixin, db.Model):
    id                                          = db.Column(db.Integer, primary_key=True)
    public_id                                   = db.Column(db.String(50), unique=True)
    name                                        = db.Column(db.String(256))
    created_at                                  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at                                  = db.Column(db.DateTime, default=datetime.utcnow)
    college_id                                  = db.Column(db.Integer, db.ForeignKey('college.id'))
    act                                         = db.Column(db.SmallInteger, default=0)
    sat                                         = db.Column(db.SmallInteger, default=0)
    amount                                      = db.Column(db.String(256), nullable=True)
    amount_expression                           = db.Column(db.String(256), nullable=True)
    unweighted_hs_gpa                           = db.Column(db.Numeric(3, 2), default=0)
    class_rank                                  = db.Column(db.String(256), nullable=True)
    status                                      = db.Column(db.String(256), nullable=True)
    relevant_information                        = db.Column(db.String(256), nullable=True)
    national_merit_finalist                     = db.Column(db.Boolean, default=False)
    graduated_spring_before_college             = db.Column(db.Boolean, default=False)
    location                                    = db.Column(db.String(256), nullable=True)
    governors_scholar_program                   = db.Column(db.Boolean, default=False)
    rogers_scholar_program                      = db.Column(db.Boolean, default=False)
    paid_full_time_christian_ministry_parent    = db.Column(db.Boolean, default=False)
    parents_higher_education                    = db.Column(db.Boolean, default=False)
    siblings_currently_in_college               = db.Column(db.Boolean, default=False)
    application_needed                          = db.Column(db.Boolean, default=False)
    scholarships_needed                         = db.Column(db.Text, nullable=True)
    ethnicity                                   = db.Column(db.String(256), nullable=True)
    first_choice_national_merit                 = db.Column(db.String(256), nullable=True)
    national_hispanic_recognition_scholar       = db.Column(db.Boolean, default=False)
    exclude                                     = db.Column(db.Boolean, default=False)
    group_by                                    = db.Column(db.Integer, nullable=True)

    ATTR_FIELDS = [
        'name',
        'act',
        'sat',
        'amount',
        'amount_expression',
        'unweighted_hs_gpa',
        'class_rank',
        'status',
        'relevant_information',
        'national_merit_finalist',
        'graduated_spring_before_college',
        'location',
        'counties',
        'not_allowed_counties',
        'not_allowed_locations',
        'governors_scholar_program',
        'rogers_scholar_program',
        'paid_full_time_christian_ministry_parent',
        'parents_higher_education',
        'siblings_currently_in_college',
        'application_needed',
        'scholarships_needed',
        'ethnicity',
        'first_choice_national_merit',
        'national_hispanic_recognition_scholar',
        'exclude',
        'group_by'
    ]

    def __repr__(self):
        return '<Scholarship {}>'.format(self.name)

    def to_dict(self):
        return {
            'public_id': self.public_id,
            'name': self.name,
            'created_at': self.created_at.isoformat() + 'Z',
            'updated_at': self.updated_at.isoformat() + 'Z',
            'act': self.act,
            'sat': self.sat,
            'amount': self.amount,
            'amount_expression': self.amount_expression,
            'unweighted_hs_gpa': str(self.unweighted_hs_gpa),
            'class_rank': self.class_rank,
            'status': self.status,
            'relevant_information': self.relevant_information,
            'national_merit_finalist': self.national_merit_finalist,
            'graduated_spring_before_college': self.graduated_spring_before_college,
            'location': self.location,
            'counties': self.counties,
            'not_allowed_counties': self.not_allowed_counties,
            'not_allowed_locations': self.not_allowed_locations,
            'governors_scholar_program': self.governors_scholar_program,
            'rogers_scholar_program': self.rogers_scholar_program,
            'paid_full_time_christian_ministry_parent': self.paid_full_time_christian_ministry_parent,
            'parents_higher_education': self.parents_higher_education,
            'siblings_currently_in_college': self.siblings_currently_in_college,
            'application_needed': self.application_needed,
            'scholarships_needed': self.scholarships_needed,
            'ethnicity': self.ethnicity,
            'first_choice_national_merit': self.first_choice_national_merit,
            'national_hispanic_recognition_scholar': self.national_hispanic_recognition_scholar,
            'exclude': self.exclude,
            'group_by': self.group_by
        }

    def from_dict(self, data):
        for field in self.ATTR_FIELDS:
            if field in data:
                setattr(self, field, data[field])
        self.updated_at = datetime.utcnow()
