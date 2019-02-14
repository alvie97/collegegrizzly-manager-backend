from hashlib import md5

from flask import url_for

from app import db, photos
from app.common.utils import generate_public_id

from .common.base_mixin import BaseMixin
from .common.date_audit import DateAudit
from .common.location_blacklist_mixin import LocationBlacklistMixin
from .common.location_mixin import LocationMixin
from .common.paginated_api_mixin import PaginatedAPIMixin
from .major import Major
from .relationship_tables import college_major


class College(PaginatedAPIMixin, DateAudit, LocationMixin,
              LocationBlacklistMixin, BaseMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(
        db.String(50), unique=True, default=generate_public_id)
    name = db.Column(db.String(256))
    room_and_board = db.Column(db.Numeric(8, 2), default=0)
    type_of_institution = db.Column(db.String(256), nullable=True)
    phone = db.Column(db.String(256), nullable=True)
    website = db.Column(db.Text, nullable=True)
    in_state_tuition = db.Column(db.Numeric(8, 2), default=0)
    out_of_state_tuition = db.Column(db.Numeric(8, 2), default=0)
    location = db.Column(db.String(256), nullable=True)
    religious_affiliation = db.Column(db.String(256), nullable=True)
    setting = db.Column(db.String(256), nullable=True)
    number_of_students = db.Column(db.Integer, default=0)
    unweighted_hs_gpa = db.Column(db.Numeric(4, 2), default=0)
    sat = db.Column(db.Integer, default=0)
    act = db.Column(db.Integer, default=0)
    __str_repr__ = "college"
    scholarships = db.relationship(
        "Scholarship",
        backref="college",
        cascade="all, delete-orphan",
        lazy="dynamic")

    pictures = db.relationship(
        "Picture",
        backref="college",
        cascade="all, delete-orphan",
        lazy="dynamic")

    majors = db.relationship(
        "Major",
        secondary=college_major,
        backref=db.backref("colleges", lazy="dynamic"),
        lazy="dynamic")

    college_details = db.relationship(
        "CollegeDetails", uselist=False, backref="college")

    submissions = db.relationship(
        "Submission", backref="college", lazy="dynamic")

    ATTR_FIELDS = [
        "name", "room_and_board", "type_of_institution", "phone", "website",
        "in_state_tuition", "out_of_state_tuition", "location",
        "religious_affiliation", "setting", "number_of_students",
        "unweighted_hs_gpa", "sat", "act"
    ]

    def __repr__(self):
        return "<College {}>".format(self.name)

    def add_major(self, major: Major):
        if not self.has_major(major.name):
            self.majors.append(major)

    def remove_major(self, major: Major):
        if self.has_major(major.name):
            self.majors.remove(major)

    def has_major(self, major_name):
        return self.majors.filter(Major.name == major_name).count() > 0

    def get_majors(self):

        return [major.to_dict() for major in self.majors.all()]

    def get_avatar(self, size):
        digest = md5("test@email.com".encode("utf-8")).hexdigest()
        return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(
            digest, size)

    def total_ofs(self):
        return self.room_and_board + self.out_of_state_tuition

    def total_is(self):
        return self.room_and_board + self.in_state_tuition

    def get_logo(self):
        logo = self.pictures.filter_by(type="logo").first()

        if logo is None:
            return self.get_avatar(128)

        return photos.url(logo.name)

    def delete(self):
        pics = self.pictures.all()

        for pic in pics:
            pic.delete()

        db.session.delete(self)

    def for_pagination(self):
        return {
            "name": self.name,
            "public_id": self.public_id,
            **self.audit_dates(), "logo": self.get_logo(),
            "_links": {
                "get_college":
                url_for("colleges.get_college", public_id=self.public_id)
            }
        }

    def to_dict(self):
        return {
            "public_id": self.public_id,
            "editable_fields": {
                "name": self.name,
                "room_and_board": str(self.room_and_board),
                "type_of_institution": self.type_of_institution,
                "phone": self.phone,
                "website": self.website,
                "in_state_tuition": str(self.in_state_tuition),
                "out_of_state_tuition": str(self.out_of_state_tuition),
                "location": self.location,
                "religious_affiliation": self.religious_affiliation,
                "setting": self.setting,
                "number_of_students": self.number_of_students,
                "unweighted_hs_gpa": str(self.unweighted_hs_gpa),
                "sat": self.sat,
                "act": self.act
            },
            "logo": self.get_logo(),
            "majors": self.get_majors(),
            "_links": {
                "scholarships":
                url_for(
                    "colleges.get_college_scholarships",
                    public_id=self.public_id),
                "pictures":
                url_for("pictures.get_pictures", public_id=self.public_id),
                "in_state_requirement":
                self.location_requirement_endpoints(
                    "colleges", "college", public_id=self.public_id)
            }
        }
