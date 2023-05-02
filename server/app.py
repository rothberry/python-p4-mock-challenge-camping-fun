#!/usr/bin/env python3

from flask import Flask, request
from flask_migrate import Migrate
# from flask_restful import Api, Resource
from ipdb import set_trace

from models import db, Activity, Signup, Camper

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
# api = Api(app)


@app.route('/')
def home():
    return ''

# class Campers(Resource):
#     # index
#     def get(self):
#         pass
# api.add_resource(Campers, "/campers")

# campers#index, show, create
@app.route("/campers", methods=["GET", "POST"])
def campers():
    # index
    # FInd all the campers
    # Then map all the campers to a dict
    # return the json
    if request.method == "GET":
        all_campers = Camper.query.all()
        response = [ cmp.to_dict(rules=("-activities", "-signups", "-created_at", "-updated_at")) for cmp in all_campers]
        return response,  200
    elif request.method == "POST":
        form_data = request.get_json()
        try:
            camper = Camper(name=form_data.get('name'), age=form_data["age"])
            db.session.add(camper)
            db.session.commit()
            return camper.to_dict(), 201
        except ValueError as err:
            return {"error": err.args[0]}, 400

@app.route("/campers/<int:id>")
def camper_by_id(id):
    camper = Camper.query.filter(Camper.id == id).one_or_none()
    if camper:
        return camper.to_dict()
        # return camper.to_dict(rules=("-signups",))
        # return camper.activities_dict()
    return {"error": f"Camper of id: {id} Not Found"}, 404

# act#index, delete
@app.route("/activities")
def activities():
    all_acts = Activity.query.all()
    response = [ cmp.to_dict(rules=("-campers", "-signups", "-created_at", "-updated_at")) for cmp in all_acts]
    return response,  200

@app.route("/activities/<int:id>", methods=["DELETE"])
def act_by_id(id):
    act = Activity.query.filter_by(id=id).one_or_none()
    if act:
        db.session.delete(act)
        db.session.commit()
        return {}, 204
    return {"error": f"Act of id: {id} Not Found"}, 404

# signups#create
@app.route("/signups", methods=["POST"])
def signups():
    form_data = request.get_json()
    try:
        signup = Signup(
            time=form_data.get("time"),
            camper_id=form_data.get("camper_id"),
            activity_id=form_data.get("activity_id"),
        )
        db.session.add(signup)
        db.session.commit()
        return signup.activity.to_dict(), 201
    except ValueError as err:
        return {"error": err.args[0]}, 422



if __name__ == '__main__':
    app.run(port=5555, debug=True)
