import flask
import flask_sqlalchemy
import flask_migrate
import config
import flask_cors
import flask_uploads

db = flask_sqlalchemy.SQLAlchemy()
migrate = flask_migrate.Migrate()
cors = flask_cors.CORS(resources={r"/api/*": {"origins": "*"}})
photos = flask_uploads.UploadSet('photos', flask_uploads.IMAGES)


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

    from app import auth
    from app import site
    from app.api import colleges
    from app.api import scholarships
    from app.api import users
    from app.api import submissions
    from app.api import majors
    from app.api import details
    from app.api import programs
    from app.api import qualification_rounds
    from app.api import questions
    from app.api import grades

    app.register_blueprint(colleges.bp, url_prefix="/api/colleges")
    app.register_blueprint(scholarships.bp, url_prefix="/api/scholarships")
    app.register_blueprint(majors.bp, url_prefix="/api/majors")
    app.register_blueprint(qualification_rounds.bp, url_prefix="/api/qualification_rounds")
    app.register_blueprint(programs.bp, url_prefix="/api/programs")
    app.register_blueprint(grades.bp, url_prefix="/api/grades")
    app.register_blueprint(users.bp, url_prefix="/api/users")
    app.register_blueprint(submissions.bp, url_prefix="/api/submissions")
    app.register_blueprint(questions.bp, url_prefix="/api/questions")
    app.register_blueprint(details.bp, url_prefix="/api/details")

    app.register_blueprint(auth.bp, url_prefix="/auth")
    app.register_blueprint(site.bp)

    return app


from app import models
