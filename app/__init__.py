import flask
import flask_sqlalchemy
import flask_migrate
import config
import flask_cors
import flask_uploads
import flask_jwt_extended

db = flask_sqlalchemy.SQLAlchemy()
migrate = flask_migrate.Migrate()
cors = flask_cors.CORS(resources={r"/api/*": {"origins": "*"}})
photos = flask_uploads.UploadSet('photos', flask_uploads.IMAGES)
jwt = flask_jwt_extended.JWTManager()


def create_app(config_class=config.Config):
    """Creates application instance.

    Args:
        config_class: configuration class instance.
    
    Returns:
        An instance of the application.
    """
    app = flask.Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    flask_uploads.configure_uploads(app, photos)
    jwt.init_app(app)

    from app.security import utils as security_utils
    from app import auth
    # from app import site
    from app.api import colleges
    from app.api import scholarships
    from app.api import users
    from app.api import submissions
    from app.api import majors
    from app.api import details
    from app.api import programs
    from app.api import qualification_rounds
    from app.api import questions
    from app.api import options
    from app.api import grades
    from app.api import grade_requirement_groups

    security_utils.protect_blueprint(colleges.bp)
    app.register_blueprint(colleges.bp, url_prefix="/api/colleges")

    security_utils.protect_blueprint(scholarships.bp)
    app.register_blueprint(scholarships.bp, url_prefix="/api/scholarships")

    security_utils.protect_blueprint(majors.bp)
    app.register_blueprint(majors.bp, url_prefix="/api/majors")

    security_utils.protect_blueprint(qualification_rounds.bp)
    app.register_blueprint(
        qualification_rounds.bp, url_prefix="/api/qualification_rounds")

    security_utils.protect_blueprint(programs.bp)
    app.register_blueprint(programs.bp, url_prefix="/api/programs")

    security_utils.protect_blueprint(grades.bp)
    app.register_blueprint(grades.bp, url_prefix="/api/grades")

    security_utils.protect_blueprint(users.bp)
    app.register_blueprint(users.bp, url_prefix="/api/users")

    security_utils.protect_blueprint(submissions.bp)
    app.register_blueprint(submissions.bp, url_prefix="/api/submissions")

    security_utils.protect_blueprint(questions.bp)
    app.register_blueprint(questions.bp, url_prefix="/api/questions")

    security_utils.protect_blueprint(options.bp)
    app.register_blueprint(options.bp, url_prefix="/api/options")

    security_utils.protect_blueprint(details.bp)
    app.register_blueprint(details.bp, url_prefix="/api/details")

    security_utils.protect_blueprint(grade_requirement_groups.bp)
    app.register_blueprint(
        grade_requirement_groups.bp,
        url_prefix="/api/grade_requirement_groups")

    app.register_blueprint(auth.bp, url_prefix="/auth")

    # app.register_blueprint(site.bp)

    from app.errors import error_404

    app.register_error_handler(404, error_404)

    return app


from app import models
