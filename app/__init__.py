from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from .gabeWhoosh import MyWhooshSearch

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)

    mysearch = MyWhooshSearch()
    mysearch.index()
    app.mysearch = mysearch

    # Register routes blueprint
    from .routes import main
    app.register_blueprint(main)

    return app
