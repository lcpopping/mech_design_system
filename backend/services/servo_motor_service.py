"""Servo motor selection service."""
from typing import Dict, List, Optional
from backend.models.servo_motor import ServoMotor, ServoMotorType
from backend.calculations.servo_motor_calc import ServoMotorCalculator, FRICTION_COEFFICIENTS, TRANSMISSION_EFFICIENCY
from backend.app import db


class ServoMotorService:
    """Service for servo motor selection."""

    @staticmethod
    def get_servo_motor_types() -> List[Dict]:
        """Get all servo motor types."""
        types = ServoMotorType.query.all()
        return [t.to_dict() for t in types]

    @staticmethod
    def query_servo_motors(
        power_min_w: float = None,
        power_max_w: float = None,
        torque_min_nm: float = None,
        torque_max_nm: float = None
    ) -> List[Dict]:
        """Query servo motors with optional filters."""
        query = ServoMotor.query

        if power_min_w is not None:
            query = query.filter(ServoMotor.power_w >= power_min_w)
        if power_max_w is not None:
            query = query.filter(ServoMotor.power_w <= power_max_w)
        if torque_min_nm is not None:
            query = query.filter(ServoMotor.rated_torque_nm >= torque_min_nm)
        if torque_max_nm is not None:
            query = query.filter(ServoMotor.rated_torque_nm <= torque_max_nm)

        motors = query.order_by(ServoMotor.power_w).all()
        return [m.to_dict() for m in motors]

    @staticmethod
    def get_servo_motor_by_id(motor_id: int) -> Optional[Dict]:
        """Get servo motor details by ID."""
        motor = ServoMotor.query.get(motor_id)
        return motor.to_dict() if motor else None

    @staticmethod
    def intelligent_select(
        load_mass_kg: float,
        speed_ms: float = 0,
        speed_rpm: int = 0,
        motion_type: str = 'linear',
        guide_type: str = 'linear_guide',
        wheel_radius_m: float = 0.05,
        screw_lead_m: float = 0.005,
        safety_factor: float = 1.2,
        load_type: str = 'h',
        transmission_type: str = 'direct',
        reduction_ratio: float = 1.0,
        friction_coefficient: float = 0.1,
        duty_cycle: str = 'S1',
        inertia_matching_limit: float = 5
    ) -> Dict:
        """Intelligently select best servo motor based on load requirements.

        Args:
            load_mass_kg: Load mass in kg
            speed_ms: Linear speed in m/s (for linear motion)
            speed_rpm: Rotational speed in rpm (for rotary motion)
            motion_type: 'linear', 'rotary', or 'ball_screw'
            guide_type: Type of linear guide
            wheel_radius_m: Wheel/drum radius for rotary (m)
            screw_lead_m: Ball screw lead (m)
            safety_factor: Safety factor for torque
            load_type: 'h' (horizontal), 't' (inclined), 'v' (vertical)
            transmission_type: 'direct', 'belt', 'ball_screw', 'planetary_screw', 'rack'
            reduction_ratio: Gear/reduction ratio
            friction_coefficient: Friction coefficient
            duty_cycle: 'S1', 'S2', 'S3', 'S5'
            inertia_matching_limit: Maximum JL/JM ratio (3, 5, or 10)

        Returns:
            Selection results with candidates ranked
        """
        # Get friction coefficient based on guide type
        if friction_coefficient <= 0:
            friction_coeff = FRICTION_COEFFICIENTS.get(guide_type, 0.1)
        else:
            friction_coeff = friction_coefficient

        # Calculate load forces
        forces = ServoMotorCalculator.calculate_load_forces(
            load_mass_kg=load_mass_kg,
            load_type=load_type,
            friction_coefficient=friction_coeff
        )

        # Calculate motor speed
        motor_speed_rpm = ServoMotorCalculator.calculate_motor_speed(
            linear_speed_ms=speed_ms,
            transmission_type=transmission_type,
            screw_lead_m=screw_lead_m,
            reduction_ratio=reduction_ratio
        )

        # Get transmission efficiency
        transmission_efficiency = TRANSMISSION_EFFICIENCY.get(transmission_type, 0.9)

        # Calculate required torque
        required_torque_nm = ServoMotorCalculator.calculate_torque(
            total_force_n=forces['fT'],
            transmission_type=transmission_type,
            screw_lead_m=screw_lead_m,
            wheel_radius_m=wheel_radius_m,
            reduction_ratio=reduction_ratio,
            efficiency=transmission_efficiency
        )

        # Calculate load inertia
        load_inertia_kgm2 = ServoMotorCalculator.calculate_load_inertia(
            load_mass_kg=load_mass_kg,
            transmission_type=transmission_type,
            screw_lead_m=screw_lead_m,
            wheel_radius_m=wheel_radius_m
        )

        # Calculate required power
        required_power_kw = ServoMotorCalculator.calculate_required_power(
            total_force_n=forces['fT'],
            linear_speed_ms=speed_ms,
            safety_factor=safety_factor
        )

        required_power_w = required_power_kw * 1000

        # Find suitable servo motors
        min_torque = required_torque_nm * safety_factor
        min_power_w = required_power_w * 0.9 if required_power_w > 0 else 0

        # Query motors that meet requirements
        candidates = ServoMotor.query.filter(
            ServoMotor.rated_torque_nm >= min_torque * 0.8,
            ServoMotor.power_w >= min_power_w * 0.8
        ).order_by(ServoMotor.rated_torque_nm).all()

        if not candidates:
            # If no exact match, get the smallest available
            candidates = ServoMotor.query.order_by(ServoMotor.rated_torque_nm).limit(10).all()

        rated_candidates = []
        for motor in candidates:
            # Check suitability including inertia matching
            check = ServoMotorCalculator.check_servo_suitability(
                servo_torque_nm=motor.rated_torque_nm,
                servo_max_torque_nm=motor.max_torque_nm,
                servo_speed_rpm=motor.rated_speed_rpm,
                servo_inertia_kgm2=motor.inertia_kgm2,
                required_speed_rpm=motor_speed_rpm,
                required_torque_nm=required_torque_nm,
                required_inertia_kgm2=load_inertia_kgm2,
                safety_factor=safety_factor,
                inertia_matching_limit=inertia_matching_limit,
                duty_cycle=duty_cycle
            )

            # Calculate score (lower is better)
            # Prefer motors that are close to requirements
            torque_diff = abs(motor.rated_torque_nm - required_torque_nm * safety_factor) / (required_torque_nm * safety_factor) if required_torque_nm > 0 else 1
            inertia_diff = abs(check['inertia_ratio'] - 1) / inertia_matching_limit if check['inertia_ratio'] > 0 else 0
            score = torque_diff * 2 + inertia_diff + (0.5 if not check['speed_ok'] else 0) + (1 if not check['passed'] else 0)

            rated_candidates.append({
                'motor': motor.to_dict(),
                'required_torque_nm': required_torque_nm,
                'required_power_kw': required_power_kw,
                'required_power_w': required_power_w,
                'required_speed_rpm': motor_speed_rpm,
                'load_inertia_kgm2': load_inertia_kgm2,
                'suitability_check': check,
                'score': score,
                'calculation_details': {
                    'fG': forces['fG'],
                    'fF': forces['fF'],
                    'fT': forces['fT'],
                    'load_type': load_type,
                    'transmission_type': transmission_type,
                    'transmission_efficiency': transmission_efficiency
                }
            })

        # Sort by score (lower is better)
        rated_candidates.sort(key=lambda x: x['score'])

        recommended = rated_candidates[0] if rated_candidates else None

        return {
            'required_torque_nm': required_torque_nm,
            'required_power_kw': required_power_kw,
            'required_power_w': required_power_w,
            'required_speed_rpm': motor_speed_rpm,
            'load_inertia_kgm2': load_inertia_kgm2,
            'motion_type': motion_type,
            'load_type': load_type,
            'transmission_type': transmission_type,
            'candidates': rated_candidates[:5],
            'recommended': recommended,
            'input': {
                'load_mass_kg': load_mass_kg,
                'speed_ms': speed_ms,
                'speed_rpm': speed_rpm,
                'motion_type': motion_type,
                'guide_type': guide_type,
                'wheel_radius_m': wheel_radius_m,
                'screw_lead_m': screw_lead_m,
                'safety_factor': safety_factor,
                'load_type': load_type,
                'transmission_type': transmission_type,
                'reduction_ratio': reduction_ratio,
                'friction_coefficient': friction_coeff,
                'duty_cycle': duty_cycle,
                'inertia_matching_limit': inertia_matching_limit
            }
        }