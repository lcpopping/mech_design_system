"""Bearing calculation engine - ISO 281/ISO 76 standards."""
import math
from typing import Dict, Optional

# Reliability factors (Weibull distribution)
RELIABILITY_FACTORS = {
    0.90: 1.0,      # L10
    0.95: 1.57,    # L5
    0.96: 1.86,    # L4
    0.97: 2.21,    # L3
    0.98: 2.74,    # L2
    0.99: 3.63,    # L1
}

# Temperature factors for different materials
MATERIAL_TEMP_FACTORS = {
    'steel': {'factor': 1.0, 'max_temp': 150},  # Chrome steel
    'stainless': {'factor': 0.7, 'max_temp': 120},
    'ceramic': {'factor': 0.6, 'max_temp': 100},
}

# Lubrication factors (统一在此定义)
LUBRICATION_FACTORS = {
    'grease': 0.7,
    'oil_bath': 0.9,
    'oil_mist': 0.8,
    'oil': 1.0,  # 循环油润滑
}

# X, Y factors for equivalent load calculation (ISO 281)
# 根据Fa/Fr比值和轴承类型确定
EQUIVALENT_LOAD_FACTORS = {
    'deep_groove': [
        {'fa/fr_max': 0.014, 'e': 0.019, 'x': 1, 'y': 0},
        {'fa/fr_max': 0.029, 'e': 0.028, 'x': 1, 'y': 0},
        {'fa/fr_max': 0.057, 'e': 0.056, 'x': 1, 'y': 0},
        {'fa/fr_max': 0.086, 'e': 0.084, 'x': 1, 'y': 0},
        {'fa/fr_max': 0.114, 'e': 0.111, 'x': 1, 'y': 0},
        {'fa/fr_max': 0.171, 'e': 0.139, 'x': 0.56, 'y': 1.8},
        {'fa/fr_max': 0.229, 'e': 0.183, 'x': 0.56, 'y': 2.4},
        {'fa/fr_max': 0.286, 'e': 0.223, 'x': 0.56, 'y': 3.0},
        {'fa/fr_max': 999, 'e': 0.222, 'x': 0.56, 'y': 3.6},
    ],
    'angular_contact': [
        {'fa/fr_max': 999, 'e': 0.68, 'x': 0.45, 'y': 1.0},
    ],
    'tapered_roller': [
        {'fa/fr_max': 999, 'e': 0.4, 'x': 0.4, 'y': 1.6},
    ],
    'thrust_ball': [
        {'fa/fr_max': 999, 'e': 0, 'x': 1, 'y': 0},
    ],
    'self_aligning': [
        {'fa/fr_max': 999, 'e': 0, 'x': 1, 'y': 0},
    ],
    'cylindrical_roller': [
        {'fa/fr_max': 999, 'e': 0, 'x': 1, 'y': 0},
    ],
}


class BearingCalculator:
    """Bearing calculation engine based on ISO 281 and ISO 76."""

    @staticmethod
    def calculate_basic_life(c: float, p: float, n: float) -> Dict:
        """Calculate L10 basic rating life.

        Args:
            c: Basic dynamic load rating (N)
            p: Equivalent dynamic load (N)
            n: Rotational speed (rpm)

        Returns:
            L10 life in hours and revolutions
        """
        if p <= 0 or n <= 0:
            return {'error': 'Load and speed must be positive'}
        if c <= 0:
            return {'error': 'Dynamic load rating must be positive'}

        l10_millions = math.pow(c / p, 3)  # Basic rating life in millions of revolutions
        l10_hours = (l10_millions * 1e6) / (n * 60)

        return {
            'l10_life_millions': l10_millions,
            'l10_life_hours': l10_hours,
            'input': {'C': c, 'P': p, 'n': n}
        }

    @staticmethod
    def calculate_modified_life(
        c: float,
        p: float,
        n: float,
        reliability: float = 0.9,
        temperature: float = 70,
        lubrication_factor: float = 0.7,
        contamination_factor: float = 1.0
    ) -> Dict:
        """Calculate L10m modified rating life (ISO 281).

        Args:
            c: Basic dynamic load rating (N)
            p: Equivalent dynamic load (N)
            n: Rotational speed (rpm)
            reliability: Reliability factor (default 0.9 for L10)
            temperature: Operating temperature (°C)
            lubrication_factor: Lubrication condition factor (0.5-1.0)
            contamination_factor: Contamination factor (0.5-1.0)

        Returns:
            Modified L10m life with all correction factors
        """
        if p <= 0 or n <= 0:
            return {'error': 'Load and speed must be positive'}
        if c <= 0:
            return {'error': 'Dynamic load rating must be positive'}

        # Reliability factor a1
        a1 = RELIABILITY_FACTORS.get(reliability, 1.0)

        # Temperature factor a_temp (simplified)
        # For steel bearings, capacity decreases above 120°C
        if temperature <= 120:
            a_temp = 1.0
        elif temperature <= 150:
            a_temp = 1.0 - 0.01 * (temperature - 120)
        else:
            a_temp = 0.7 - 0.002 * (temperature - 150)
        a_temp = max(0.3, a_temp)  # Minimum 30%

        # Composite correction factor a_ISO
        # a_ISO = a1 * a2 * a3 where a2=lubrication, a3=contamination
        a_iso = a1 * lubrication_factor * contamination_factor * a_temp

        # Basic life in millions
        l10_millions = math.pow(c / p, 3)

        # Modified life
        l10m_millions = a_iso * l10_millions
        l10m_hours = (l10m_millions * 1e6) / (n * 60)

        # Life adjustment ratio
        life_ratio = l10m_hours / ((l10_millions * 1e6) / (n * 60)) if n > 0 else 0

        return {
            'l10m_life_millions': l10m_millions,
            'l10m_life_hours': l10m_hours,
            'reliability_factor_a1': a1,
            'temperature_factor': a_temp,
            'lubrication_factor': lubrication_factor,
            'contamination_factor': contamination_factor,
            'composite_factor_a_iso': a_iso,
            'life_ratio': life_ratio,
            'input': {
                'C': c,
                'P': p,
                'n': n,
                'reliability': reliability,
                'temperature': temperature
            }
        }

    @staticmethod
    def calculate_required_rating(
        p: float,
        n: float,
        required_life_hours: float,
        reliability: float = 0.9,
        temperature: float = 70,
        lubrication_factor: float = 0.7,
        contamination_factor: float = 1.0
    ) -> Dict:
        """Calculate required dynamic load rating for given requirements.

        Args:
            p: Equivalent dynamic load (N)
            n: Rotational speed (rpm)
            required_life_hours: Required L10 life in hours
            reliability: Reliability factor
            temperature: Operating temperature (°C)
            lubrication_factor: Lubrication factor
            contamination_factor: Contamination factor

        Returns:
            Required dynamic load rating C_required
        """
        if p <= 0 or required_life_hours <= 0:
            return {'error': 'Invalid parameters'}

        # Calculate composite factor
        a1 = RELIABILITY_FACTORS.get(reliability, 1.0)

        if temperature <= 120:
            a_temp = 1.0
        elif temperature <= 150:
            a_temp = 1.0 - 0.01 * (temperature - 120)
        else:
            a_temp = 0.7 - 0.002 * (temperature - 150)
        a_temp = max(0.3, a_temp)

        a_iso = a1 * lubrication_factor * contamination_factor * a_temp

        # From L10m = a_iso * (C/P)^3 * 10^6
        # Solving for C: C = P * (L10m / a_iso)^(1/3)
        required_millions = (required_life_hours * n * 60) / 1e6
        c_required = p * math.pow(required_millions / a_iso, 1.0 / 3.0)

        return {
            'required_dynamic_load_rating': c_required,
            'required_life_hours': required_life_hours,
            'composite_factor': a_iso,
            'input': {
                'P': p,
                'n': n,
                'reliability': reliability,
                'temperature': temperature
            }
        }

    @staticmethod
    def check_static_load(
        c0: float,
        fr: float,
        fa: float,
        x0: float = 1.0,
        y0: float = 0.0,
        safety_factor: float = 1.0
    ) -> Dict:
        """Check static load capacity (ISO 76).

        Args:
            c0: Basic static load rating (N)
            fr: Radial load (N)
            fa: Axial load (N)
            x0: Radial factor
            y0: Axial factor

        Returns:
            Static load check results
        """
        if c0 <= 0:
            return {'error': 'Static load rating must be positive'}

        # Equivalent static load
        p0 = x0 * fr + y0 * fa

        # Safety factor
        s0 = c0 / p0 if p0 > 0 else float('inf')
        passed = s0 >= safety_factor

        return {
            'equivalent_static_load': p0,
            'safety_factor': s0,
            'required_safety': safety_factor,
            'passed': passed,
            'input': {'C0': c0, 'Fr': fr, 'Fa': fa, 'X0': x0, 'Y0': y0}
        }

    @staticmethod
    def calculate_stiffness(
        bearing_type: str,
        c: float,
        bore_diameter: float
    ) -> Dict:
        """Estimate bearing stiffness.

        Args:
            bearing_type: 'deep_groove', 'angular_contact', 'tapered_roller'
            c: Dynamic load rating (N)
            bore_diameter: Bore diameter (mm)

        Returns:
            Radial and axial stiffness values
        """
        # Simplified stiffness estimation
        # Real values depend on bearing series and preload

        # Base stiffness proportional to load rating
        # Deep groove ball bearings: stiffer axially
        # Roller bearings: stiffer radially

        if bearing_type == 'deep_groove':
            # Ball bearings - higher radial stiffness
            k_radial = c / 1500  # N/μm
            k_axial = c / 2500
        elif bearing_type == 'angular_contact':
            # Angular contact - similar in both directions
            k_radial = c / 1800
            k_axial = c / 1800
        elif bearing_type == 'tapered_roller':
            # Roller bearings - higher radial, lower axial
            k_radial = c / 800
            k_axial = c / 3000
        else:
            k_radial = c / 1500
            k_axial = c / 2500

        # Adjust for bore diameter
        size_factor = (bore_diameter or 50) / 50  # Normalized to 50mm
        k_radial *= size_factor
        k_axial *= size_factor

        return {
            'radial_stiffness_N_per_um': k_radial,
            'axial_stiffness_N_per_um': k_axial,
            'type': bearing_type,
            'bore_diameter_mm': bore_diameter
        }

    @staticmethod
    def calculate_equivalent_load(
        fr: float,
        fa: float,
        bearing_type: str = 'deep_groove'
    ) -> float:
        """Calculate equivalent dynamic load using ISO 281 X, Y factors.

        Args:
            fr: Radial load (N)
            fa: Axial load (N)
            bearing_type: Bearing type for factor lookup

        Returns:
            Equivalent load P
        """
        if fr <= 0:
            return fa if fa > 0 else 0

        fa_fr_ratio = fa / fr

        # Get factors for bearing type
        factors = EQUIVALENT_LOAD_FACTORS.get(bearing_type, EQUIVALENT_LOAD_FACTORS['deep_groove'])

        # Find appropriate X, Y based on fa/fr ratio
        x, y = 1, 0  # default for pure radial
        for f in factors:
            if fa_fr_ratio <= f['fa/fr_max']:
                x, y = f['x'], f['y']
                break

        # If fa/fr > e, use combined formula
        e = factors[0]['e'] if factors else 0
        if fa_fr_ratio <= e:
            return fr
        else:
            return x * fr + y * fa

    @staticmethod
    def get_bearing_type_defaults(bearing_type: str) -> Dict:
        """Get default parameters for bearing type.

        Args:
            bearing_type: 'deep_groove', 'angular_contact', 'tapered_roller'

        Returns:
            Default X0, Y0, e values for static load calculation
        """
        defaults = {
            'deep_groove': {
                'x0': 1.0, 'y0': 0.0, 'e': 0.0,
                'description': '深沟球轴承，适用于高速、轻载'
            },
            'angular_contact': {
                'x0': 0.5, 'y0': 0.46, 'e': 0.68,
                'description': '角接触球轴承，可承受联合载荷'
            },
            'tapered_roller': {
                'x0': 0.5, 'y0': 0.67, 'e': 0.4,
                'description': '圆锥滚子轴承，承载能力强'
            },
            'thrust_ball': {
                'x0': 1.0, 'y0': 0.0, 'e': 0.0,
                'description': '推力球轴承，纯轴向载荷'
            },
            'self_aligning': {
                'x0': 1.0, 'y0': 0.0, 'e': 0.0,
                'description': '调心球轴承，可补偿轴不对中'
            },
            'cylindrical_roller': {
                'x0': 1.0, 'y0': 0.0, 'e': 0.0,
                'description': '圆柱滚子轴承，高径向载荷'
            }
        }
        return defaults.get(bearing_type, defaults['deep_groove'])
