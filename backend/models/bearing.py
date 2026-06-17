"""Bearing database model."""
from datetime import datetime
from backend.app import db

class BearingType(db.Model):
    __tablename__ = 'bearing_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'code': self.code}

class Bearing(db.Model):
    __tablename__ = 'bearings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_id = db.Column(db.Integer, db.ForeignKey('bearing_types.id'))
    model = db.Column(db.String(50), nullable=False, unique=True)
    bore_diameter = db.Column(db.Float, nullable=False)
    outer_diameter = db.Column(db.Float, nullable=False)
    width = db.Column(db.Float, nullable=False)
    dynamic_load_rating = db.Column(db.Float, nullable=False)
    static_load_rating = db.Column(db.Float, nullable=False)
    max_speed = db.Column(db.Float)
    weight = db.Column(db.Float)
    standard = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'model': self.model, 'type_id': self.type_id,
            'bore_diameter': self.bore_diameter, 'outer_diameter': self.outer_diameter,
            'width': self.width, 'dynamic_load_rating': self.dynamic_load_rating,
            'static_load_rating': self.static_load_rating, 'max_speed': self.max_speed,
            'weight': self.weight, 'standard': self.standard
        }
