"""Servo motor database model."""
from datetime import datetime
from backend.app import db


class ServoMotorType(db.Model):
    __tablename__ = 'servo_motor_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(200))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description
        }


class ServoMotor(db.Model):
    __tablename__ = 'servo_motors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_id = db.Column(db.Integer, db.ForeignKey('servo_motor_types.id'))
    model = db.Column(db.String(50), nullable=False, unique=True)
    power_w = db.Column(db.Float, nullable=False)
    rated_torque_nm = db.Column(db.Float, nullable=False)
    max_torque_nm = db.Column(db.Float, nullable=False)
    rated_speed_rpm = db.Column(db.Integer, nullable=False)
    max_speed_rpm = db.Column(db.Integer, nullable=False)
    inertia_kgm2 = db.Column(db.Float)
    voltage_v = db.Column(db.Integer, default=220)
    rated_current_a = db.Column(db.Float)
    frame_size = db.Column(db.String(20))
    shaft_diameter = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    brake = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'model': self.model,
            'type_id': self.type_id,
            'power_w': self.power_w,
            'power_kw': self.power_w / 1000,
            'rated_torque_nm': self.rated_torque_nm,
            'max_torque_nm': self.max_torque_nm,
            'rated_speed_rpm': self.rated_speed_rpm,
            'max_speed_rpm': self.max_speed_rpm,
            'inertia_kgm2': self.inertia_kgm2,
            'voltage_v': self.voltage_v,
            'rated_current_a': self.rated_current_a,
            'frame_size': self.frame_size,
            'shaft_diameter': self.shaft_diameter,
            'weight_kg': self.weight_kg,
            'brake': self.brake
        }