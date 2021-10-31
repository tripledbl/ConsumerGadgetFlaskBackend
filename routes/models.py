from . import routes

@routes.route('/models')
def models():
    return "hello from models"