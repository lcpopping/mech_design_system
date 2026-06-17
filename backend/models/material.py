"""Material database model."""
from datetime import datetime
from backend.app import db

class Material(db.Model):
    __tablename__ = 'materials'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    grade = db.Column(db.String(100))
    density = db.Column(db.Float)
    youngs_modulus = db.Column(db.Float)
    yield_strength = db.Column(db.Float)
    tensile_strength = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'grade': self.grade,
            'density': self.density, 'youngs_modulus': self.youngs_modulus,
            'yield_strength': self.yield_strength, 'tensile_strength': self.tensile_strength
        }
