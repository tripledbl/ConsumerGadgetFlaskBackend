from flask import Blueprint
from bson.objectid import ObjectId
from dataIngestion import retrieveSquareOrdersData

modelRoutes = Blueprint('modelRoutes', __name__)


# createModel
# create a machine learning model using predetermined data and inputs
@modelRoutes.route('/createModel/<string:user_id>', methods=['GET'])
def createModel(user_id):

    # get the orders data from the users square account
    res = retrieveSquareOrdersData(user_id)

    return res
