from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
import psycopg2

app = Flask(__name__)
db = SQLAlchemy()
login_manager = LoginManager()

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    DB_URI = 'postgresql+psycopg2://postgres:123456@localhost:5432/finalproject'
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = '123456'

    db.app = app
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'login'

    from .route import app as main_blueprint
    app.register_blueprint(main_blueprint)

    # Verify database connection
    try:
        conn = get_db_connection()
        conn.close()
        print("Database connection successful.")
    except Exception as e:
        print(f"Database connection failed: {e}")

    return app

def get_db_connection():
    conn = psycopg2.connect(
        dbname='finalproject',
        user='postgres',
        password='123456',
        host='localhost',
        port='5432'
    )
    return conn