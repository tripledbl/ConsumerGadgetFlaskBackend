import os
import json
from flask_pymongo import PyMongo
from flask import Flask, Blueprint, jsonify, request, current_app, Response
from bson import json_util
from bson.objectid import ObjectId
from datetime import datetime, timedelta

mongo_client = PyMongo()
