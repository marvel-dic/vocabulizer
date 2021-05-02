from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# init SQLAlchemy so we can use it later in our models
from vocabulizer.etl.config import DATABASE_URI

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    # cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.config['SECRET_KEY'] = 'j2pQUKC0xqIB9DT4jI3R'
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
