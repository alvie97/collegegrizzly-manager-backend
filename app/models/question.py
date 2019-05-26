import app
import flask
from app.models.common import base_mixin, paginated_api_mixin, date_audit
from app.models import option as option_model
from app.models import association_tables


class Question(app.db.Model, base_mixin.BaseMixin,
               paginated_api_mixin.PaginatedAPIMixin, date_audit.DateAudit):
    """Question model.

    Attributes:
        id (integer): model id.
        name (string): question name.
    """
    id = app.db.Column(app.db.Integer, primary_key=True)
    name = app.db.Column(app.db.String(256), unique=True, index=True)
    options = app.db.relationship(
        "Option",
        secondary=association_tables.question_option,
        backref=app.db.backref("questions", lazy="dynamic"),
        lazy="dynamic")

    str_repr = "question"

    def has_option(self, option_id):
        """checks if question has option.

        Args:
            self (class): question class.
            option_id (int): option id.
        Returns:
            Boolean: true if question has option, false otherwise.

        """
        return self.options.filter(association_tables.question_option.c.
                                   option_id == option_id).count() > 0

    def add_option(self, option):
        """Adds option to question.

        Args:
            self (class): question class.
            option (sqlalchemy.Model): option object.
        """
        if not self.has_option(option.id):
            self.options.append(option)

    def remove_option(self, option):
        """Removes option to question.

        Args:
            self (class): question class.
            option (sqlalchemy.Model): option object.
        """
        if self.has_option(option.id):
            self.options.remove(option)

    def __repr__(self):
        return f"<Question {self.name}>"

    def for_pagination(self):
        return self.to_dict()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "links": {
                "get_options": flask.url_for(
                    "questions.get_options", id=self.id)
            }
        }
