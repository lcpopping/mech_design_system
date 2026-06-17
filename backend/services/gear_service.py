"""Gear service."""
from backend.calculations.gear_calc import GearCalculator

class GearService:
    @staticmethod
    def calculate_geometry(module, teeth, pressure_angle=20.0, helix_angle=0.0):
        return GearCalculator.calculate_geometry(module, teeth, pressure_angle, helix_angle)

    @staticmethod
    def check_strength(module, teeth, face_width, torque, speed_rpm, pressure_angle=20.0, helix_angle=0.0):
        geo = GearCalculator.calculate_geometry(module, teeth, pressure_angle, helix_angle)
        if 'error' in geo:
            return geo
        d = geo['pitch_diameter']
        f = (torque * 1000) / (d / 2)
        v = math.pi * d * speed_rpm / (60 * 1000)
        sigma_h = 500 * math.sqrt(f / (face_width * d))
        sigma_f = f / (face_width * module * 0.3)
        contact_check = GearCalculator.check_contact_strength(sigma_h, 1200)
        bending_check = GearCalculator.check_bending_strength(sigma_f, 300)
        return {
            'geometry': geo,
            'contact_stress_mpa': sigma_h,
            'bending_stress_mpa': sigma_f,
            'contact_safety_factor': contact_check.get('safety_factor'),
            'bending_safety_factor': bending_check.get('safety_factor'),
            'contact_passed': contact_check.get('passed'),
            'bending_passed': bending_check.get('passed')
        }
