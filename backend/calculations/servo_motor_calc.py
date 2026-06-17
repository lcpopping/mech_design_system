"""Servo motor calculation engine - based on reference implementation from recycle bin."""
import math
from typing import Dict, List, Optional

# Friction coefficients for different guide types
FRICTION_COEFFICIENTS = {
    'linear_guide': 0.05,      # Linear guide with recirculating balls
    'slide_guide': 0.15,       # Plain slide guide
    'ball_screw': 0.1,         # Ball screw efficiency factor
    'roller_guide': 0.03,       # Roller guide
    'direct': 0.0,             # Direct (no guide friction)
    'belt': 0.02,             # Belt transmission
    'gear': 0.05,             # Gear transmission
}

# Transmission efficiency
TRANSMISSION_EFFICIENCY = {
    'direct': 0.98,             # Direct coupling
    'belt': 0.95,              # Belt/同步带 transmission
    'ball_screw': 0.9,         # Ball screw (force to torque conversion)
    'planetary_screw': 0.85,   # Planetary screw
    'rack': 0.9,               # Rack and pinion
}

# Duty cycle factors (for torque derating)
DUTY_CYCLE_FACTORS = {
    'S1': 1.0,    # Continuous duty
    'S2': 1.4,    # Short-time duty
    'S3': 1.2,    # Periodic duty
    'S5': 1.3,    # Periodic duty with starting
}

# Inertia matching limits
INERTIA_MATCHING_LIMITS = {
    3: 3,    # High precision
    5: 5,    # Medium precision (default)
    10: 10,  # Low precision
}


class ServoMotorCalculator:
    """Servo motor selection calculator based on reference implementation."""

    @staticmethod
    def calculate_load_forces(
        load_mass_kg: float,
        load_type: str = 'h',  # h=horizontal, t=inclined, v=vertical
        friction_coefficient: float = 0.1,
        gravity: float = 9.81
    ) -> Dict:
        """Calculate gravitational and friction forces.

        Args:
            load_mass_kg: Load mass in kg
            load_type: 'h' (horizontal), 't' (inclined ~30°), 'v' (vertical)
            friction_coefficient: Friction coefficient
            gravity: Gravity acceleration m/s²

        Returns:
            Dictionary with fG (gravity force), fF (friction force), fT (total force)
        """
        # Gravity load based on direction
        if load_type == 'h':
            fG = 0  # No gravity load for horizontal motion
        elif load_type == 't':
            fG = load_mass_kg * gravity * 0.5  # Inclined (sin 30° ≈ 0.5)
        else:  # 'v' vertical
            fG = load_mass_kg * gravity

        # Friction force
        fF = load_mass_kg * friction_coefficient * gravity

        # Total force
        fT = fG + fF

        return {
            'fG': fG,
            'fF': fF,
            'fT': fT,
            'load_type': load_type
        }

    @staticmethod
    def calculate_motor_speed(
        linear_speed_ms: float,
        transmission_type: str = 'direct',
        screw_lead_m: float = 0.005,
        reduction_ratio: float = 1.0
    ) -> float:
        """Calculate motor speed (rpm) from linear speed.

        Based on reference: nM = v * 60 / (Pm * i)

        Args:
            linear_speed_ms: Linear speed in m/s
            transmission_type: 'direct', 'belt', 'ball_screw', 'planetary_screw', 'rack'
            screw_lead_m: Lead/pitch for screw or rack (in meters)
            reduction_ratio: Reduction ratio (i)

        Returns:
            Motor speed in rpm
        """
        if transmission_type == 'direct':
            # For direct drive with drum/wheel: nM = v * 60 / (2πr * i)
            # With r = 0.1m default, equivalent Pm = 2π * 0.1 = 0.628m
            equivalent_lead = 2 * math.pi * 0.1  # Default wheel radius 0.1m
        elif transmission_type in ('ball_screw', 'planetary_screw'):
            equivalent_lead = screw_lead_m
        elif transmission_type == 'belt':
            # Belt/pulley: use wheel radius from screw_lead_m (belt pitch)
            equivalent_lead = screw_lead_m if screw_lead_m > 0 else 0.01
        elif transmission_type == 'rack':
            # Rack: pitch circle circumference = π * module * teeth
            equivalent_lead = screw_lead_m if screw_lead_m > 0 else 0.01
        else:
            equivalent_lead = 0.01  # Default 10mm pitch

        i = max(reduction_ratio, 0.001)
        nM = linear_speed_ms * 60 / (equivalent_lead * i)
        return nM

    @staticmethod
    def calculate_torque(
        total_force_n: float,
        transmission_type: str = 'direct',
        screw_lead_m: float = 0.005,
        wheel_radius_m: float = 0.1,
        reduction_ratio: float = 1.0,
        efficiency: float = 0.9
    ) -> float:
        """Calculate required torque (Nm).

        Based on reference: T = fT * Pm / (2 * π * i) / 1000

        Args:
            total_force_n: Total force in N
            transmission_type: Type of transmission
            screw_lead_m: Lead for screw transmission (m)
            wheel_radius_m: Radius for direct/belt drive (m)
            reduction_ratio: Gear/reduction ratio
            efficiency: Transmission efficiency

        Returns:
            Torque in Nm
        """
        i = max(reduction_ratio, 0.001)

        if transmission_type == 'direct':
            # Torque = Force × Radius
            r = wheel_radius_m if wheel_radius_m > 0 else 0.1
            torque = total_force_n * r / i / efficiency
        elif transmission_type in ('ball_screw', 'planetary_screw'):
            # Torque = Force × Lead / (2π × i × efficiency)
            lead = screw_lead_m if screw_lead_m > 0 else 0.005
            torque = total_force_n * lead / (2 * math.pi * i * efficiency)
        elif transmission_type == 'belt':
            # Torque = Force × pitch_radius / i
            r = wheel_radius_m if wheel_radius_m > 0 else 0.05
            torque = total_force_n * r / i / efficiency
        elif transmission_type == 'rack':
            # Rack: torque = Force × pitch_diameter / (2 × i)
            pitch_d = screw_lead_m if screw_lead_m > 0 else 0.02
            torque = total_force_n * pitch_d / (2 * i) / efficiency
        else:
            # Default: direct coupling
            torque = total_force_n * 0.1 / i / efficiency

        return torque

    @staticmethod
    def calculate_load_inertia(
        load_mass_kg: float,
        transmission_type: str = 'direct',
        screw_lead_m: float = 0.005,
        wheel_radius_m: float = 0.1
    ) -> float:
        """Calculate load inertia (kg·m²).

        Based on reference: J = m × (Pm / 2π)² / 10⁶

        Args:
            load_mass_kg: Load mass in kg
            transmission_type: Type of transmission
            screw_lead_m: Lead for screw transmission (m)
            wheel_radius_m: Radius for direct/belt (m)

        Returns:
            Load inertia in kg·m²
        """
        if transmission_type == 'direct':
            # Equivalent radius = wheel radius
            r = wheel_radius_m if wheel_radius_m > 0 else 0.1
        elif transmission_type in ('ball_screw', 'planetary_screw'):
            # Equivalent radius = lead / (2π)
            lead = screw_lead_m if screw_lead_m > 0 else 0.005
            r = lead / (2 * math.pi)
        elif transmission_type == 'belt':
            r = wheel_radius_m if wheel_radius_m > 0 else 0.05
        elif transmission_type == 'rack':
            r = screw_lead_m / (2 * math.pi) if screw_lead_m > 0 else 0.01
        else:
            r = 0.1

        # J = m × r² (in kg·m²)
        j = load_mass_kg * r * r / 1e6  # Convert mm² to m²
        return j

    @staticmethod
    def calculate_required_power(
        total_force_n: float,
        linear_speed_ms: float,
        safety_factor: float = 1.2
    ) -> float:
        """Calculate required power (kW).

        Uses direct power calculation: P = F * v

        Args:
            total_force_n: Total force in N
            linear_speed_ms: Linear speed in m/s
            safety_factor: Safety factor

        Returns:
            Required power in kW
        """
        if linear_speed_ms <= 0:
            return 0
        # P (W) = F (N) × v (m/s)
        power_w = total_force_n * linear_speed_ms
        # Convert to kW with safety factor
        power_kw = power_w / 1000 * safety_factor
        if power_kw < 0:
            power_kw = abs(power_kw)
        return power_kw

    @staticmethod
    def calculate_linear_power(
        load_mass_kg: float,
        speed_ms: float,
        friction_coefficient: float = 0.1
    ) -> float:
        """Calculate power required for linear motion.

        Args:
            load_mass_kg: Load mass in kg
            speed_ms: Speed in m/s
            friction_coefficient: Friction coefficient

        Returns:
            Required power in W
        """
        force_n = load_mass_kg * 9.81 * friction_coefficient
        return force_n * speed_ms  # Power = Force × Velocity

    @staticmethod
    def calculate_rotary_torque(
        load_mass_kg: float,
        wheel_radius_m: float,
        friction_coefficient: float = 0.1
    ) -> float:
        """Calculate torque required for rotary motion (wheel/drum drive).

        Args:
            load_mass_kg: Load mass in kg
            wheel_radius_m: Wheel radius in meters
            friction_coefficient: Friction coefficient

        Returns:
            Required torque in Nm
        """
        force_n = load_mass_kg * 9.81 * friction_coefficient
        return force_n * wheel_radius_m  # Torque = Force × Radius

    @staticmethod
    def calculate_rotary_power(
        load_mass_kg: float,
        wheel_radius_m: float,
        speed_rpm: float,
        friction_coefficient: float = 0.1
    ) -> float:
        """Calculate power required for rotary motion.

        Args:
            load_mass_kg: Load mass in kg
            wheel_radius_m: Wheel radius in meters
            speed_rpm: Rotational speed rpm
            friction_coefficient: Friction coefficient

        Returns:
            Required power in W
        """
        torque_nm = ServoMotorCalculator.calculate_rotary_torque(load_mass_kg, wheel_radius_m, friction_coefficient)
        # Power (W) = Torque (Nm) × ω (rad/s) = Torque × 2π × n / 60
        power_w = torque_nm * 2 * math.pi * speed_rpm / 60
        return power_w

    @staticmethod
    def calculate_ball_screw_torque(
        load_mass_kg: float,
        screw_lead_m: float,
        efficiency: float = 0.9
    ) -> float:
        """Calculate torque required for ball screw drive.

        Args:
            load_mass_kg: Load mass in kg (including work piece)
            screw_lead_m: Ball screw lead in meters
            efficiency: Ball screw efficiency (typically 0.9)

        Returns:
            Required torque in Nm
        """
        # Force = mass × g
        force_n = load_mass_kg * 9.81
        # Torque = Force × Lead / (2π × efficiency)
        torque = force_n * screw_lead_m / (2 * math.pi * efficiency)
        return torque

    @staticmethod
    def calculate_required_torque_from_power(
        power_w: float,
        speed_rpm: float
    ) -> float:
        """Calculate torque from power and speed.

        Args:
            power_w: Power in Watts
            speed_rpm: Speed in rpm

        Returns:
            Torque in Nm
        """
        if speed_rpm <= 0:
            return 0
        # P = T × ω = T × 2π × n / 60
        # T = P × 60 / (2π × n)
        return power_w * 60 / (2 * math.pi * speed_rpm)

    @staticmethod
    def check_servo_suitability(
        servo_torque_nm: float,
        servo_max_torque_nm: float,
        servo_speed_rpm: int,
        servo_inertia_kgm2: float,
        required_speed_rpm: float,
        required_torque_nm: float,
        required_inertia_kgm2: float,
        safety_factor: float = 1.2,
        inertia_matching_limit: float = 5,
        duty_cycle: str = 'S1'
    ) -> Dict:
        """Check if servo motor is suitable for the application.

        Args:
            servo_torque_nm: Servo rated torque Nm
            servo_max_torque_nm: Servo max torque Nm
            servo_speed_rpm: Servo rated speed rpm
            servo_inertia_kgm2: Servo rotor inertia kg·m²
            required_speed_rpm: Required operating speed rpm
            required_torque_nm: Required torque Nm
            required_inertia_kgm2: Load inertia reflected to motor kg·m²
            safety_factor: Safety factor for torque
            inertia_matching_limit: Maximum JL/JM ratio (default 5)
            duty_cycle: Duty cycle type (S1, S2, S3, S5)

        Returns:
            Check result dictionary
        """
        required_with_safety = required_torque_nm * safety_factor

        # Torque check
        torque_ok = servo_torque_nm >= required_with_safety

        # Speed check
        speed_ok = servo_speed_rpm >= required_speed_rpm

        # Inertia matching check
        if servo_inertia_kgm2 and servo_inertia_kgm2 > 0:
            inertia_ratio = required_inertia_kgm2 / servo_inertia_kgm2
            inertia_ok = inertia_ratio <= inertia_matching_limit
        else:
            inertia_ratio = 0
            inertia_ok = True

        # Duty cycle factor
        duty_factor = DUTY_CYCLE_FACTORS.get(duty_cycle, 1.0)
        torque_allowed = servo_torque_nm * duty_factor * 0.8  # 80% of rated torque under duty

        # Torque ratio
        torque_ratio = servo_torque_nm / required_with_safety if required_with_safety > 0 else float('inf')

        passed = torque_ok and speed_ok and inertia_ok

        return {
            'passed': passed,
            'torque_ok': torque_ok,
            'speed_ok': speed_ok,
            'inertia_ok': inertia_ok,
            'torque_ratio': torque_ratio,
            'inertia_ratio': inertia_ratio,
            'inertia_matching_limit': inertia_matching_limit,
            'torque_allowed_nm': torque_allowed,
            'duty_cycle': duty_cycle,
            'duty_factor': duty_factor,
            'servo_torque_nm': servo_torque_nm,
            'servo_max_torque_nm': servo_max_torque_nm,
            'servo_speed_rpm': servo_speed_rpm,
            'servo_inertia_kgm2': servo_inertia_kgm2,
            'required_torque_nm': required_torque_nm,
            'required_with_safety_nm': required_with_safety,
            'required_speed_rpm': required_speed_rpm,
            'required_inertia_kgm2': required_inertia_kgm2,
            'safety_factor': safety_factor,
            'rating': 'excellent' if torque_ratio >= 1.5 and speed_ok and inertia_ok else
                     ('good' if passed else 'inadequate')
        }