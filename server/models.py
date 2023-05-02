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

class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    serialize_rules = ("-signups.activity", "-campers.activities")

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    # signups = db.relationship("Signup", backref="activity")
    signups = db.relationship("Signup", back_populates="activity")
    campers = association_proxy("signups", "camper", 
                                creator=lambda cmp: Signup(camper=cmp))
    
    def my_to_dict(self):
        return {
            "name": self.name,
            "difficulty": self.difficulty,
            "campers": [cmp.my_to_dict() for cmp in self.campers],
        }

class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    serialize_rules = ("-activity.signups", "-camper.signups")

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)

    camper_id = db.Column(db.Integer, db.ForeignKey("campers.id"))
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"))

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    activity = db.relationship("Activity", back_populates="signups")
    camper = db.relationship("Camper", back_populates="signups")

    @validates("time")
    def validates_time(self, key, time):
        if 0 <= time <= 23:
            return time
        raise ValueError("Time must be between 0 and 23")

class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    serialize_rules = ("-signups.camper", "-activities.campers")

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())


    # signups = db.relationship("Signup", backref="camper")
    signups = db.relationship("Signup", back_populates="camper")
    activities = association_proxy("signups", "activity",
                                   creator=lambda act: Signup(activity=act))
    # creator=lamba optional?
    # All the association_proxy
    # >>> [ s.activity for s in Camper.query.first().signups ]

    @validates("name")
    def validates_name(self, key, name):
        if name:
            return name
        raise ValueError("Camper must have a name")
    
    @validates("age")
    def validates_age(self, key, age):
        if age in range(8,19):
            return age
        raise ValueError("Age must be between 8 and 18")

    def activities_dict(self):
        camper_dict = self.to_dict(rules=("-signups",))
        camper_dict["activities"] = [ act.to_dict(rules=("-signups",)) for act in self.activities ]
        return camper_dict
    
    def my_to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
        }


    def my_activities(self):
        return [ s.activity for s in self.signups ]


# add any models you may need. 