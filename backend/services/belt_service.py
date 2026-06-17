"""Belt drive service."""
from backend.calculations.belt_calc import BeltCalculator

class BeltService:
    @staticmethod
    def select_section(power_kw, speed_rpm, small_diameter):
        return BeltCalculator.select_belt_section(power_kw, speed_rpm, small_diameter)

    @staticmethod
    def calculate(small_diameter, large_diameter, center_distance, power_kw, speed_rpm):
        belt_length = BeltCalculator.calculate_belt_length(small_diameter, large_diameter, center_distance)
        speed_ratio = BeltCalculator.calculate_speed_ratio(small_diameter, large_diameter)
        tension = BeltCalculator.calculate_tension(power_kw, small_diameter, speed_rpm)
        return {
            'belt_length': belt_length,
            'speed_ratio': speed_ratio,
            'large_speed': speed_rpm / speed_ratio if speed_ratio else 0,
            'tight_side_tension_N': tension.get('tight_side_tension_N', 0),
            'slack_side_tension_N': tension.get('slack_side_tension_N', 0),
            'belt_velocity_mps': tension.get('belt_velocity_mps', 0)
        }
