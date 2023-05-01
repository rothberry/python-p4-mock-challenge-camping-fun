from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)
# A Camper has many Signups, and has many Activitys through Signups
# An Activity has many Signups, and has many has many Campers through Signups
# A Signup belongs to a Camper and belongs to a Activity


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    signups = db.relationship("Signup", backref="activity")


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    camper_id = db.Column(db.Integer, db.ForeignKey("campers.id"))
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"))
    time = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    def my_to_dict(self):
        return {
            "id": self.id,
            "time": self.time,
        }

    @validates("time")
    def validates_time(self, key, value):
        if value not in range(0, 24):
            raise ValueError("Must be between 0 and 23")
        return value


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    age = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    signups = db.relationship("Signup", backref="camper")

    def my_to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age
        }
    
    def to_dict_with_assocication(self):
        camper_dict = self.my_to_dict()
        camper_dict["signups"] = [ signup.activity.to_dict() for signup in self.signups]
        return camper_dict

    @validates("name")
    def validates_name(self, key, value):
        if not value:
            raise ValueError("Can't be blank")
        return value

    @validates('age')
    def validates_age(self, key, value):
        if value not in range(8, 19):
            raise ValueError("Must be between 8 and 18")
        return value


# add any models you may need.
