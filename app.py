import os

from flask import Flask
from flask_cors import CORS
import random

# create and configure the app
app = Flask(__name__)
CORS(app)

@app.route('/hello')
def hello():
    return 'Your random ID is ' + str(random.randint(10000000,99999999))

app.run(debug=True,port=3001)