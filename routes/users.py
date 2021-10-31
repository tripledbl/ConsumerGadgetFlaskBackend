from . import routes

@routes.route('/users')
def users():
    return 'hello world from users'