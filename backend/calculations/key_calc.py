"""Key calculation engine - verified against Excel 机械设计各种计算公式.xls"""
import math
from typing import Dict, Optional

# Key material allowables (MPa)
KEY_MATERIAL_ALLOWABLES = {
    'carbon_steel': {'shear': 90, 'compression': 110, 'description': '碳钢'},
    'alloy_steel': {'shear': 130, 'compression': 150, 'description': '合金钢'},
    'stainless': {'shear': 70, 'compression': 90, 'description': '不锈钢'},
}

# Standard key section sizes (GB/T 1096-2003)
STANDARD_KEY_SIZES = [
    {'b': 2, 'h': 2, 'k': 1},
    {'b': 3, 'h': 3, 'k': 1.5},
    {'b': 4, 'h': 4, 'k': 2},
    {'b': 5, 'h': 5, 'k': 2.5},
    {'b': 6, 'h': 6, 'k': 3},
    {'b': 8, 'h': 7, 'k': 3.5},
    {'b': 10, 'h': 8, 'k': 4},
    {'b': 12, 'h': 8, 'k': 4},
    {'b': 14, 'h': 9, 'k': 4.5},
    {'b': 16, 'h': 10, 'k': 5},
    {'b': 18, 'h': 11, 'k': 5.5},
    {'b': 20, 'h': 12, 'k': 6},
    {'b': 22, 'h': 14, 'k': 7},
    {'b': 25, 'h': 14, 'k': 7},
    {'b': 28, 'h': 16, 'k': 8},
    {'b': 32, 'h': 18, 'k': 9},
    {'b': 36, 'h': 20, 'k': 10},
    {'b': 40, 'h': 22, 'k': 11},
    {'b': 45, 'h': 25, 'k': 12.5},
    {'b': 50, 'h': 28, 'k': 14},
]


class KeyCalculator:
    """Key strength calculation engine based on mechanical design standards."""

    @staticmethod
    def calculate_shear_stress(T_Nm: float, D_mm: float, b_mm: float, l_mm: float) -> float:
        """Calculate key shear stress.

        Formula: τ = 2T / (D × b × l)

        Args:
            T_Nm: Torque (N·m)
            D_mm: Shaft diameter (mm)
            b_mm: Key width (mm)
            l_mm: Key length (mm)

        Returns:
            Shear stress in MPa
        """
        if D_mm <= 0 or b_mm <= 0 or l_mm <= 0:
            return 0.0
        # Convert N·m to N·mm for consistent units: T_Nm * 1000
        return 2 * T_Nm * 1000 / (D_mm * b_mm * l_mm)

    @staticmethod
    def calculate_compression_stress(T_Nm: float, D_mm: float, k_mm: float, l_mm: float) -> float:
        """Calculate key compression/bearing stress.

        Formula: σ = 2T / (D × k × l)
        where k = h/2 is the key working height

        Args:
            T_Nm: Torque (N·m)
            D_mm: Shaft diameter (mm)
            k_mm: Key working height (mm), typically h/2
            l_mm: Key length (mm)

        Returns:
            Compression stress in MPa
        """
        if D_mm <= 0 or k_mm <= 0 or l_mm <= 0:
            return 0.0
        return 2 * T_Nm * 1000 / (D_mm * k_mm * l_mm)

    @staticmethod
    def check_key_strength(
        T_Nm: float,
        D_mm: float,
        b_mm: float,
        h_mm: float,
        l_mm: float,
        material: str = 'carbon_steel',
        safety_factor: float = 1.0
    ) -> Dict:
        """Check key strength under given torque.

        Verified formulas from Excel:
        - Compression: P = 2T / (D × k × l), k = h/2
        - Shear: τ = 2T / (D × b × l)

        Args:
            T_Nm: Torque (N·m)
            D_mm: Shaft diameter (mm)
            b_mm: Key width (mm)
            h_mm: Key height (mm)
            l_mm: Key length (mm)
            material: Key material key
            safety_factor: Safety factor to apply

        Returns:
            Dictionary with calculation results
        """
        k_mm = h_mm / 2  # Working height is half of key height

        shear_stress = KeyCalculator.calculate_shear_stress(T_Nm, D_mm, b_mm, l_mm)
        compression_stress = KeyCalculator.calculate_compression_stress(T_Nm, D_mm, k_mm, l_mm)

        # Get allowable stresses
        allowables = KEY_MATERIAL_ALLOWABLES.get(material, KEY_MATERIAL_ALLOWABLES['carbon_steel'])
        tau_allow = allowables['shear'] / safety_factor
        sigma_allow = allowables['compression'] / safety_factor

        shear_passed = shear_stress <= tau_allow
        compression_passed = compression_stress <= sigma_allow

        return {
            'input': {
                'torque_Nm': T_Nm,
                'shaft_diameter_mm': D_mm,
                'key_width_mm': b_mm,
                'key_height_mm': h_mm,
                'key_length_mm': l_mm,
                'material': material,
                'safety_factor': safety_factor
            },
            'results': {
                'working_height_k_mm': k_mm,
                'shear_stress_MPa': round(shear_stress, 2),
                'compression_stress_MPa': round(compression_stress, 2),
                'shear_allowable_MPa': round(tau_allow, 2),
                'compression_allowable_MPa': round(sigma_allow, 2),
                'shear_passed': shear_passed,
                'compression_passed': compression_passed,
                'overall_passed': shear_passed and compression_passed
            },
            'material_info': allowables
        }

    @staticmethod
    def recommend_key_length(T_Nm: float, D_mm: float, b_mm: float, h_mm: float,
                            material: str = 'carbon_steel', safety_factor: float = 1.0,
                            constraint: str = 'shear') -> float:
        """Recommend minimum key length based on constraint.

        Args:
            T_Nm: Torque (N·m)
            D_mm: Shaft diameter (mm)
            b_mm: Key width (mm)
            h_mm: Key height (mm)
            material: Key material
            safety_factor: Safety factor
            constraint: 'shear' or 'compression'

        Returns:
            Minimum recommended key length in mm
        """
        allowables = KEY_MATERIAL_ALLOWABLES.get(material, KEY_MATERIAL_ALLOWABLES['carbon_steel'])
        k_mm = h_mm / 2

        if constraint == 'shear':
            tau_allow = allowables['shear'] / safety_factor
            # From τ = 2T/(D×b×l), solve for l:
            # l = 2T / (D × b × τ_allow)
            l_min = 2 * T_Nm * 1000 / (D_mm * b_mm * tau_allow)
        else:  # compression
            sigma_allow = allowables['compression'] / safety_factor
            # From σ = 2T/(D×k×l), solve for l:
            # l = 2T / (D × k × σ_allow)
            l_min = 2 * T_Nm * 1000 / (D_mm * k_mm * sigma_allow)

        return round(l_min, 1)

    @staticmethod
    def get_standard_key_sizes(D_mm: float) -> list:
        """Get standard key sizes for given shaft diameter.

        Args:
            D_mm: Shaft diameter (mm)

        Returns:
            List of standard key size dictionaries
        """
        # Filter keys suitable for the shaft diameter
        suitable = []
        for key in STANDARD_KEY_SIZES:
            # Key b dimension should be less than shaft diameter
            if key['b'] < D_mm:
                suitable.append(key)
        return suitable