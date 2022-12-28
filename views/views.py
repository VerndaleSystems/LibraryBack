from application import app
from flask import render_template
import requests
from utils.neo_connector import neo_connect

session = neo_connect()


@app.route('/')
def index():
    #r = r.json()

    return render_template("index.html")



