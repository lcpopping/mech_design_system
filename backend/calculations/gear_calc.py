"""Gear calculation engine - ISO 6336."""
import math

class GearCalculator:
    @staticmethod
    def calculate_geometry(module, teeth, pressure_angle=20.0, helix_angle=0.0):
        """Calculate gear geometric parameters."""
        if teeth < 2:
            return {'error': 'Teeth must be >= 2'}
        if module <= 0:
            return {'error': 'Module must be positive'}

        m, z = module, teeth
        alpha = math.radians(pressure_angle)
        beta = math.radians(helix_angle)
        mt = m / math.cos(beta) if beta != 0 else m
        d = mt * z
        db = d * math.cos(alpha)
        ha, hf = m, 1.25 * m
        da = d + 2 * ha
        df = d - 2 * hf

        return {
            'module': m, 'teeth': z, 'pitch_diameter': d, 'base_diameter': db,
            'tip_diameter': da, 'root_diameter': df, 'addendum': ha, 'dedendum': hf
        }

    @staticmethod
    def check_contact_strength(sigma_h, sigma_h_allowable):
        """Check contact strength safety factor."""
        if sigma_h <= 0 or sigma_h_allowable <= 0:
            return {'error': 'Invalid stress values'}
        sf = sigma_h_allowable / sigma_h
        return {'safety_factor': sf, 'passed': sf >= 1.0}

    @staticmethod
    def check_bending_strength(sigma_f, sigma_f_allowable):
        """Check bending strength safety factor."""
        if sigma_f <= 0 or sigma_f_allowable <= 0:
            return {'error': 'Invalid stress values'}
        sf = sigma_f_allowable / sigma_f
        return {'safety_factor': sf, 'passed': sf >= 1.0}
