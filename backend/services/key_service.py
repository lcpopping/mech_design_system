"""Key selection and verification service."""
from backend.calculations.key_calc import KeyCalculator

# Material options for API
MATERIAL_OPTIONS = [
    {'code': 'carbon_steel', 'name': '碳钢', 'shear': 90, 'compression': 110},
    {'code': 'alloy_steel', 'name': '合金钢', 'shear': 130, 'compression': 150},
    {'code': 'stainless', 'name': '不锈钢', 'shear': 70, 'compression': 90},
]


class KeyService:
    """Service for key selection and strength verification."""

    @staticmethod
    def check_key_strength(
        torque_Nm: float,
        shaft_diameter_mm: float,
        key_width_mm: float,
        key_height_mm: float,
        key_length_mm: float,
        material: str = 'carbon_steel',
        safety_factor: float = 1.0
    ) -> dict:
        """Check key strength under given torque.

        Args:
            torque_Nm: Torque in N·m
            shaft_diameter_mm: Shaft diameter in mm
            key_width_mm: Key width in mm
            key_height_mm: Key height in mm
            key_length_mm: Key length in mm
            material: Material code ('carbon_steel', 'alloy_steel', 'stainless')
            safety_factor: Safety factor (default 1.0)

        Returns:
            Dictionary with check results
        """
        result = KeyCalculator.check_key_strength(
            T_Nm=torque_Nm,
            D_mm=shaft_diameter_mm,
            b_mm=key_width_mm,
            h_mm=key_height_mm,
            l_mm=key_length_mm,
            material=material,
            safety_factor=safety_factor
        )

        # Add material options to result
        result['material_options'] = MATERIAL_OPTIONS

        return result

    @staticmethod
    def recommend_key_length(
        torque_Nm: float,
        shaft_diameter_mm: float,
        key_width_mm: float,
        key_height_mm: float,
        material: str = 'carbon_steel',
        safety_factor: float = 1.0,
        constraint: str = 'shear'
    ) -> dict:
        """Recommend minimum key length.

        Args:
            torque_Nm: Torque in N·m
            shaft_diameter_mm: Shaft diameter in mm
            key_width_mm: Key width in mm
            key_height_mm: Key height in mm
            material: Material code
            safety_factor: Safety factor
            constraint: 'shear' or 'compression'

        Returns:
            Dictionary with recommended length
        """
        l_min = KeyCalculator.recommend_key_length(
            T_Nm=torque_Nm,
            D_mm=shaft_diameter_mm,
            b_mm=key_width_mm,
            h_mm=key_height_mm,
            material=material,
            safety_factor=safety_factor,
            constraint=constraint
        )

        return {
            'torque_Nm': torque_Nm,
            'shaft_diameter_mm': shaft_diameter_mm,
            'key_width_mm': key_width_mm,
            'key_height_mm': key_height_mm,
            'constraint': constraint,
            'recommended_length_mm': l_min,
            'input': {
                'material': material,
                'safety_factor': safety_factor
            }
        }

    @staticmethod
    def get_material_options() -> list:
        """Get available key materials."""
        return MATERIAL_OPTIONS

    @staticmethod
    def get_standard_key_sizes(shaft_diameter_mm: float) -> list:
        """Get standard key sizes for a given shaft diameter."""
        return KeyCalculator.get_standard_key_sizes(shaft_diameter_mm)