from . import userRoutes

@userRoutes.route('/users')
def users():
    return 'hello world from users'