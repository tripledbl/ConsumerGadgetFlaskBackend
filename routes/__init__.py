from flask import Blueprint

routes = Blueprint('routes', __name__)

from .users import *
from .models import *
