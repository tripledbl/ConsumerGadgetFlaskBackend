import os
import json
from flask_pymongo import PyMongo
from flask import Flask, Blueprint, jsonify, request, current_app
from bson import json_util
from bson.objectid import ObjectId

mongo_client = PyMongo()
