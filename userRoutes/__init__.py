from flask import Blueprint
userRoutes = Blueprint('userRoutes', __name__)

from .users import *

