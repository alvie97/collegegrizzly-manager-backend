import app
from app.models.common import base_mixin, date_audit, paginated_api_mixin


class Location(app.db.Model, base_mixin.BaseMixin,
               paginated_api_mixin.PaginatedAPIMixin, date_audit.DateAudit):
    """
        Location model.

        Attributes:
            id (integer): model id.
            state (string): location state.
            county (string): location county.
            place (string): location place.
            zip_code (string): location zip code.
    """

    id = app.db.Column(app.db.Integer, primary_key=True)
    state = app.db.Column(app.db.String(256), nullable=True)
    county = app.db.Column(app.db.String(256), nullable=True)
    place = app.db.Column(app.db.String(256), nullable=True)
    zip_code = app.db.Column(app.db.String(256), nullable=True)
    blacklist = app.db.Column(app.db.Boolean, nullable=True)
    scholarship_id = app.db.Column(app.db.Integer,
                                   app.db.ForeignKey("scholarship.id"))
    college_id = app.db.Column(app.db.Integer, app.db.ForeignKey("college.id"))

    def __repr__(self):
        state = self.state if self.state is not None else ""
        county = self.county if self.county is not None else ""
        place = self.place if self.place is not None else ""
        zip_code = self.zip_code if self.zip_code is not None else ""

        return f"<Location {state}, {county}, {place}, {zip_code}>"
