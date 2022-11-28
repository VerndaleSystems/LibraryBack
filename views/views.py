from application import app
from flask import render_template
import requests
from utils.neo_connector import neo_connect

session = neo_connect()


@app.route('/')
def index():
    r = requests.get('http://ec2-54-78-245-86.eu-west-1.compute.amazonaws.com:8090/v1/list-todays-batch-jobs').json()
    #r = r.json()

    return render_template("index.html", r=r)



