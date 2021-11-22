import os
from routes.userRoutes import *
from routes.squareRoutes import *
from routes.modelRoutes import *
from flask import Flask
from extensions import mongo_client


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # configure MongoDB database parameters
    app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
    app.config['FLASK_ENV'] = os.environ.get('FLASK_ENV')  
    app.config['SQUARE_CLIENT_ID'] = os.environ.get('SQUARE_CLIENT_ID')
    app.config['SQUARE_CLIENT_SECRET'] = os.environ.get('SQUARE_CLIENT_SECRET')
    app.config['CRABTREE_USER_ID'] = os.environ.get('CRABTREE_USER_ID')

    mongo_client.init_app(app)

    # a simple page that says hello
    @app.route('/')
    def hello():
        return 'Hello World from ConsumerGadget Backend!'

    # register all blueprints
    register_blueprints(app)

    return app


def register_blueprints(app):
    app.register_blueprint(userRoutes)
    app.register_blueprint(squareRoutes)
    app.register_blueprint(modelRoutes)


app = create_app()
