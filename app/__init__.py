from flask              import Flask
from flask_sqlalchemy   import SQLAlchemy
from flask_migrate      import Migrate
from config             import Config
from flask_restful      import Api
from flask_cors         import CORS

db = SQLAlchemy()
migrate = Migrate()
api = Api(prefix='/api')
cors = CORS(resources={r"/api/*": {"origins": "*"}})

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    api.init_app(app)

    return app

from app import models
