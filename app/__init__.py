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

    from app import colleges
    from app import scholarships
    from app import locations
    from app import files
    from app import pictures
    from app import users
    from app import auth
    from app import submissions
    from app import site

    app.register_blueprint(colleges.bp, url_prefix="/api/colleges")
    app.register_blueprint(scholarships.bp, url_prefix="/api/scholarships")
    app.register_blueprint(locations.bp, url_prefix="/api/locations")
    app.register_blueprint(files.bp, url_prefix="/api/files")
    app.register_blueprint(pictures.bp, url_prefix="/api/pictures")
    app.register_blueprint(users.bp, url_prefix="/api/users")
    app.register_blueprint(auth.bp, url_prefix="/auth")
    app.register_blueprint(submissions.bp, url_prefix="/api/submissions")
    app.register_blueprint(site.bp)

    return app


from app import models
