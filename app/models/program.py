#TODO: change program model, instead of having various programs with the same
# name and different round qualifications, make it so that theres only one
# program with different round qualifications.
from app import db

from .common.base_mixin import BaseMixin


class Program(db.Model, BaseMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True)
    round_qualification = db.Column(db.String(256), nullable=True)
    __str_repr__ = "program"

    ATTR_FIELDS = ["name", "round_qualification"]

    def __repr__(self):
        return "<Program {}>".format(self.name)

    def for_pagination(self):
        return self.to_dict()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "round_qualification": self.round_qualification
        }
