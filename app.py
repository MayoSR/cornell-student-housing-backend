import os
from venv import create

from flask import Flask
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return 'Your random ID is ' + str(random.randint(10000000,99999999))