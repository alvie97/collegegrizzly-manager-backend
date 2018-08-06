from app import db

class County(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    fips_code = db.Column(db.String(10), index=True, unique=True)

    ATTR_FIELDS = [ "name", "fips_code" ]

    def __repr__(self):
        return "<County {}>".format(self.name)

    def to_dict(self):
        return {
            "name": self.name,
            "fips_code": self.fips_code
        }

    def from_dict(self, data):
        for field in self.ATTR_FIELDS:
            if field in data:
                setattr(self, field, data[field])