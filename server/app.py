#!/usr/bin/env python3
from ipdb import set_trace

from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Activity, Signup, Camper

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

@app.route('/')
def home():
    return ''

# ! WITH Resource
class Campers(Resource):
    # index
    def get(self):
        campers = [camper.my_to_dict() for camper in Camper.query.all()]
        # set_trace()
        # print(campers)
        return make_response(campers, 200)
    
api.add_resource(Campers, "/campers")

class CamperWithID(Resource):
    # show
    def get(self, id):
        camper = Camper.query.filter_by(id=id).first()
        return make_response(camper.to_dict(), 200)

api.add_resource(CamperWithID, "/campers/<int:id>")



if __name__ == '__main__':
    app.run(port=5555, debug=True)
