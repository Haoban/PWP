
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from sqlalchemy import event
from sqlalchemy.engine import Engine
from flask_cors import CORS
from flask_jwt_extended import JWTManager
db = SQLAlchemy()

# Based on http://flask.pocoo.org/docs/1.0/tutorial/factory/#the-application-factory
# Modified to use Flask SQLAlchemy


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        #    SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "development.db"),
        #    SQLALCHEMY_TRACK_MODIFICATIONS=False
        DATABASE=os.path.join(app.instance_path, 'Eventhub.sqlite'),
    )
        
    app.config['SECRET_KEY'] = 'we the best'    
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db = SQLAlchemy(app)
    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Hello, World!'


    return app


app = create_app()
CORS(app)

app.app_context().push()

db.init_app(app)

db = SQLAlchemy(app)
jwt = JWTManager(app)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Import resource
from .resources.eventcollection import EventCollection
from .resources.eventitem import EventItem
from .resources.usercollection import UserCollection
from .resources.useritem import UserItem, UserLogin
from .resources.eventsbyuser import EventsByUser
from .resources.joinevent import JoinEvent

@app.route("/profiles/<resource>/")
def send_profile_html(resource):
    return "Random string"
    # return send_from_directory(app.static_folder, "{}.html".format(resource))


@app.route("/eventhub/link-relations/")
def send_link_relations_html():
    return "some string"
    # return send_from_directory(app.static_folder, "links-relations.html")



api = Api(app)
#     Add resource path
api.add_resource(EventCollection, "/api/events/")
api.add_resource(UserCollection, "/api/users/")
api.add_resource(EventItem, "/api/events/<id>/")
api.add_resource(UserItem, "/api/users/<id>/")
api.add_resource(EventsByUser, "/api/users/<user_id>/events/")
api.add_resource(JoinEvent, "/api/users/<user_id>/events/<event_id>/")
api.add_resource(UserLogin, '/api/login')