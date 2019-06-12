from flask import Flask
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('date_from')
parser.add_argument('date_to')
parser.add_argument('max_iters')
parser.add_argument('eps')


class FCMProcessor(object):
    def __init__(self, max_iters=100, eps=1e-5, date_from=None, date_to=None):
        self.max_iters = max_iters
        self.eps = eps
        self.date_from = date_from
        self.date_to = date_to

    def run(self):

    

        return ''

class FCMHandler(Resource):
    def post(self):
        args = parser.parse_args()
        print(args)
        return {  }


api.add_resource(FCMHandler, '/fcm/calculator')

if __name__ == '__main__':
    app.run(debug=True)