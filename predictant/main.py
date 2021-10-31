from predictant.settings import *
from predictant.extensions import *

#def create_app(config_object='predictant.settings'):
def create_app():
    app = Flask(__name__)

    # Establishing MONGO URI
    #app.config.from_object(config_object)
    app.config['MONGO_URI'] = 'mongodb+srv://Backend:nIPNZGrcSLhzaUsf@shard-1.x284i.mongodb.net/Predictant?retryWrites=true&w=majority'


    # initializing pymongo
    mongo.init_app(app)

    # registering blueprints found in routes folder
    app.register_blueprint(routes)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/')
    def hello():
        return 'Hello World from ConsumerGadget Backend!'

    users_collection = mongo.db.users

    @app.route("/test", methods=['POST'])
    def add_one():
        users_collection.insert_one({'status': 'test'})
        return '<h1>Added a Status!</h1>'

    return app
