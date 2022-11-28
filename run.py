#from flask_restful import Resource, Api
#from flask_cors import CORS

from utils.logger import LoggingMiddleware
from views.views import *
from views.item_routes import *
from views.user_routes import *



if __name__ == '__main__':
    app.wsgi_app = LoggingMiddleware(app.wsgi_app)
    app.run(debug=True)
