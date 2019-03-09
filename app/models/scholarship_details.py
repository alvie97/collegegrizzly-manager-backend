import app
from app.models.common import date_audit, base_mixin


class ScholarshipDetails(app.db.Model, date_audit.DateAudit,
                         base_mixin.BaseMixin):
    """Scholarship details model

    Attributes:
        id (integer): model id.
        name (string): scholarship name.
        amount (string): amount given by scholarship.
        amount_expression (string): formatted string to process the scholarship's amount
        application_needed (boolean): if scholarship needs application.
        group (string): scholarship's group.
        type (string): type of scholarship.
        scholarship_id (integer): foreign key for scholarship.
    """
    id = app.db.Column(app.db.Integer, primary_key=True)
    name = app.db.Column(app.db.String(256), unique=True, index=True)
    amount = app.db.Column(app.db.String(256))
    amount_expression = app.db.Column(app.db.String(256), nullable=True)
    application_needed = app.db.Column(app.db.Boolean, default=False)
    group = app.db.Column(app.db.String(256), nullable=True)
    description = app.db.Column(app.db.Text, nullable=True)
    type = app.db.Column(app.db.String(256), nullable=True)
    scholarship_id = app.db.Column(app.db.Integer,
                                         app.db.ForeignKey("scholarship.id"))

    str_repr = "scholarship_details"

    ATTR_FIELDS = [
        "name", "amount", "amount_expression", "application_needed", "group",
        "description", "type"
    ]

    def __repr__(self):
        return f"<Scholarship Details for Scholarship {self.name} ID: {self.scholarship.id}>"

    def to_dict(self):
        return {
            "name": self.name,
            "amount": self.amount,
            "amount_expression": self.amount_expression,
            "application_needed": self.application_needed,
            "group": self.group,
            "description": self.description,
            "type": self.type
        }
