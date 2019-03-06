import app
from app.models.common import date_audit, base_mixin


class CollegeDetails(app.db.Model, date_audit.DateAudit, base_mixin.BaseMixin):
    id = app.db.Column(app.db.Integer, primary_key=True)
    name = app.db.Column(app.db.String(256), unique=True, index=True)
    room_and_board = app.db.Column(app.db.Numeric(8, 2), nullable=True)
    type_of_institution = app.db.Column(app.db.String(256), nullable=True)
    phone = app.db.Column(app.db.String(256), nullable=True)
    website = app.db.Column(app.db.Text, nullable=True)
    in_state_tuition = app.db.Column(app.db.Numeric(8, 2), nullable=True)
    out_of_state_tuition = app.db.Column(app.db.Numeric(8, 2), nullable=True)
    location_address = app.db.Column(app.db.Text, nullable=True)
    religious_affiliation = app.db.Column(app.db.String(256), nullable=True)
    setting = app.db.Column(app.db.String(256), nullable=True)
    number_of_students = app.db.Column(app.db.Integer, nullable=True)
    college_id = app.db.Column(app.db.Integer, app.db.ForeignKey("college.id"))

    str_repr = "college_details"

    ATTR_FIELDS = [
        "room_and_board", "type_of_institution", "phone", "website",
        "in_state_tuition", "out_of_state_tuition", "location_address",
        "religious_affiliation", "setting", "number_of_students"
    ]

    def __repr__(self):
        return f"<College Details for college {self.name} ID:{self.college.id}>"

    def to_dict(self):
        return {
            "costs": {
                "room_and_board": str(self.room_and_board),
                "in_state_tuition": str(self.in_state_tuition),
                "out_of_state_tuition": str(self.out_of_state_tuition)
            },
            "type_of_institution": self.type_of_institution,
            "phone": self.phone,
            "website": self.website,
            "location_address": self.location_address,
            "religious_affiliation": self.religious_affiliation,
            "setting": self.setting,
            "number_of_students": self.number_of_students
        }
