from app import db

class Ethnicity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))

    ATTR_FIELDS = [ "name" ]

    def __repr__(self):
        return "<Ethnicity {}>".format(self.name)

    def to_dict(self):
        return { "name": self.name }

    def from_dict(self, data):
        for field in self.ATTR_FIELDS:
            if field in data:
                setattr(self, field, data[field])