import json
from flask_pymongo import PyMongo
from flask import Blueprint, jsonify, request
from bson import json_util
from bson.objectid import ObjectId
from flask import Flask

mongo_client = PyMongo()
