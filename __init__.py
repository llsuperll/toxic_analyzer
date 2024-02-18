from flask import Flask
from data import db_session
from view import view
from authorization import auth
from flask_login import LoginManager
from data.users import User

DB_NAME = "database.db"


# инициализация приложения
def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "Leha_secret"
    db_session.global_init(f"db/{DB_NAME}")

    app.register_blueprint(view, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        db_sess = db_session.create_session()
        return db_sess.query(User).get(int(user_id))

    app.run()

    return app
