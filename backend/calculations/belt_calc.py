"""Belt drive calculation engine."""
import math

class BeltCalculator:
    @staticmethod
    def calculate_belt_length(small_diameter, large_diameter, center_distance):
        """Calculate belt pitch length."""
        d1, d2, c = small_diameter, large_diameter, center_distance
        l = 2 * c + (math.pi / 2) * (d1 + d2) + math.pow(d2 - d1, 2) / (4 * c)
        return l

    @staticmethod
    def calculate_speed_ratio(diameter_small, diameter_large):
        """Calculate speed ratio."""
        return diameter_large / diameter_small

    @staticmethod
    def select_belt_section(power_kw, speed_rpm, small_diameter):
        """Select appropriate belt section."""
        power_per_rib = power_kw
        if power_per_rib <= 1.5:
            section = 'SPZ'
        elif power_per_rib <= 4:
            section = 'SPA'
        elif power_per_rib <= 15:
            section = 'SPB'
        else:
            section = 'SPC'
        min_d = {'SPZ': 63, 'SPA': 90, 'SPB': 140, 'SPC': 224}.get(section, 63)
        return {'recommended_section': section, 'min_recommended_diameter': min_d}

    @staticmethod
    def calculate_tension(power_kw, small_diameter, speed_rpm, wrap_angle=180):
        """Calculate belt tensions."""
        d = small_diameter / 1000
        v = math.pi * d * speed_rpm / 60
        if v <= 0:
            return {'error': 'Invalid speed or diameter'}
        mu, theta_rad = 0.3, math.radians(wrap_angle)
        ratio = math.exp(mu * theta_rad)
        power_nm = power_kw * 1000
        diff_tension = power_nm / v
        t2 = diff_tension / (ratio - 1)
        t1 = ratio * t2
        return {'tight_side_tension_N': t1, 'slack_side_tension_N': t2, 'belt_velocity_mps': v}
