"""Bearing service with intelligent selection."""
from typing import Dict, List, Optional
from backend.models.bearing import Bearing, BearingType
from backend.calculations.bearing_calc import BearingCalculator
from backend.app import db


class BearingService:
    """Service for bearing selection and calculation."""

    @staticmethod
    def get_bearing_types() -> List[Dict]:
        """Get all bearing types with defaults."""
        types = BearingType.query.all()
        result = []
        for t in types:
            type_code = t.code.lower() if t.code else ''
            if '6' in type_code or 'deep' in type_code.lower() or '6000' in type_code:
                bt = 'deep_groove'
            elif '7' in type_code or 'angular' in type_code.lower() or '7000' in type_code:
                bt = 'angular_contact'
            elif '3' in type_code or 'tapered' in type_code.lower() or '30200' in type_code:
                bt = 'tapered_roller'
            elif '5' in type_code or 'thrust' in type_code.lower() or '51000' in type_code:
                bt = 'thrust_ball'
            elif '12' in type_code or 'self' in type_code.lower() or '1200' in type_code:
                bt = 'self_aligning'
            elif 'n' in type_code or 'cylindrical' in type_code.lower() or 'n2000' in type_code:
                bt = 'cylindrical_roller'
            else:
                bt = 'deep_groove'

            defaults = BearingCalculator.get_bearing_type_defaults(bt)
            result.append({
                'id': t.id,
                'name': t.name,
                'code': t.code,
                'type_code': bt,
                'defaults': defaults
            })
        return result

    @staticmethod
    def query_bearings(
        bearing_type: str = None,
        bore_min: float = None,
        bore_max: float = None,
        load_min: float = None,
        speed_max: float = None
    ) -> List[Dict]:
        """Query bearings with optional filters."""
        query = Bearing.query

        # Filter by bearing type
        if bearing_type:
            type_map = {
                'deep_groove': 1,  # 6000 series
                'angular_contact': 2,  # 7000 series
                'tapered_roller': 3,  # 30200 series
                'thrust_ball': 4,  # 51000 series
                'self_aligning': 5,  # 1200 series
                'cylindrical_roller': 6,  # N2000 series
            }
            type_id = type_map.get(bearing_type.lower())
            if type_id:
                query = query.filter(Bearing.type_id == type_id)

        if bore_min:
            query = query.filter(Bearing.bore_diameter >= bore_min)
        if bore_max:
            query = query.filter(Bearing.bore_diameter <= bore_max)
        if load_min:
            query = query.filter(Bearing.dynamic_load_rating >= load_min)
        if speed_max:
            query = query.filter(Bearing.max_speed >= speed_max)

        bearings = query.order_by(Bearing.dynamic_load_rating).all()
        return [b.to_dict() for b in bearings]

    @staticmethod
    def intelligent_select(
        bearing_type: str,
        fr: float,
        fa: float,
        speed: float,
        temperature: float = 70,
        lubrication: str = 'grease',
        required_life_hours: float = 10000,
        reliability: float = 0.9,
        bore_min: float = None,
        bore_max: float = None
    ) -> Dict:
        """Intelligently select best bearing based on requirements.

        Args:
            bearing_type: 'deep_groove', 'angular_contact', 'tapered_roller'
            fr: Radial load (N)
            fa: Axial load (N)
            speed: Rotational speed (rpm)
            temperature: Operating temperature (°C)
            lubrication: Lubrication type ('grease', 'oil_bath', etc.)
            required_life_hours: Required L10 life in hours
            reliability: Reliability (0.9-0.99)
            bore_min: Minimum bore diameter (mm)
            bore_max: Maximum bore diameter (mm)

        Returns:
            Selection results with candidates ranked
        """
        # Get default factors for bearing type
        defaults = BearingCalculator.get_bearing_type_defaults(bearing_type)
        x0, y0 = defaults['x0'], defaults['y0']

        # Calculate equivalent load
        e = defaults['e']
        if fa / fr <= e if fr > 0 else False:
            p = fr
        else:
            x = 0.56  # Simplified
            y = y0
            p = x * fr + y * fa

        # Get lubrication factor
        lub_factors = {
            'grease': 0.7,
            'oil_bath': 0.9,
            'oil_mist': 0.8,
            'oil循环': 1.0,
        }
        lub_factor = lub_factors.get(lubrication.lower(), 0.7)

        # Calculate required dynamic load rating
        req_result = BearingCalculator.calculate_required_rating(
            p=p,
            n=speed,
            required_life_hours=required_life_hours,
            reliability=reliability,
            temperature=temperature,
            lubrication_factor=lub_factor
        )

        if 'error' in req_result:
            return req_result

        c_required = req_result.get('required_dynamic_load_rating', 0)

        # Query candidate bearings
        candidates = BearingService.query_bearings(
            bearing_type=bearing_type,
            bore_min=bore_min,
            bore_max=bore_max,
            load_min=c_required * 0.8,  # Allow some margin
            speed_max=speed * 1.1  # Allow 10% overspeed
        )

        if not candidates:
            return {
                'error': 'No suitable bearing found',
                'required_capacity_N': c_required,
                'bearing_type': bearing_type
            }

        # Calculate life for each candidate and rank
        rated_candidates = []
        for candidate in candidates:
            c_actual = candidate.get('dynamic_load_rating', 0)
            if c_actual < c_required:
                continue

            # Calculate modified life
            life_result = BearingCalculator.calculate_modified_life(
                c=c_actual,
                p=p,
                n=speed,
                reliability=reliability,
                temperature=temperature,
                lubrication_factor=lub_factor
            )

            if 'error' in life_result:
                continue

            l10m_hours = life_result.get('l10m_life_hours', 0)

            # Calculate static load check
            c0 = candidate.get('static_load_rating', 0)
            static_result = BearingCalculator.check_static_load(
                c0=c0, fr=fr, fa=fa, x0=x0, y0=y0, safety_factor=1.0
            )

            # Calculate stiffness
            stiffness = BearingCalculator.calculate_stiffness(
                bearing_type=bearing_type,
                c=c_actual,
                bore_diameter=candidate.get('bore_diameter', 0)
            )

            # Calculate safety factor (closer to 1 is better - more economical)
            safety_factor = c_actual / c_required if c_required > 0 else float('inf')

            # Score: lower is better (closer to ideal capacity utilization)
            score = abs(safety_factor - 1.5)  # Ideal SF around 1.5

            rated_candidates.append({
                'bearing': candidate,
                'l10m_life_hours': l10m_hours,
                'life_ratio': life_result.get('life_ratio', 0),
                'safety_factor': safety_factor,
                'static_check': static_result,
                'stiffness': stiffness,
                'score': score,
                'required_capacity': c_required
            })

        # Sort by score (lower is better)
        rated_candidates.sort(key=lambda x: x['score'])

        # Get recommended (best score)
        recommended = rated_candidates[0] if rated_candidates else None

        return {
            'required_capacity_N': c_required,
            'equivalent_load_P': p,
            'bearing_type': bearing_type,
            'composite_factor': req_result.get('composite_factor', 0),
            'candidates': rated_candidates[:5],  # Top 5 candidates
            'recommended': recommended,
            'input': {
                'Fr': fr,
                'Fa': fa,
                'speed': speed,
                'temperature': temperature,
                'lubrication': lubrication,
                'required_life_hours': required_life_hours,
                'reliability': reliability
            }
        }

    @staticmethod
    def get_bearing_by_id(bearing_id: int) -> Optional[Dict]:
        """Get bearing details by ID."""
        bearing = Bearing.query.get(bearing_id)
        return bearing.to_dict() if bearing else None

    @staticmethod
    def calculate_full_spec(
        bearing_id: int,
        fr: float,
        fa: float,
        speed: float,
        temperature: float = 70,
        lubrication: str = 'grease',
        reliability: float = 0.9
    ) -> Dict:
        """Calculate full specifications for selected bearing.

        Args:
            bearing_id: Selected bearing ID
            fr: Radial load (N)
            fa: Axial load (N)
            speed: Rotational speed (rpm)
            temperature: Operating temperature (°C)
            lubrication: Lubrication type
            reliability: Reliability

        Returns:
            Full calculation results
        """
        bearing = Bearing.query.get(bearing_id)
        if not bearing:
            return {'error': 'Bearing not found'}

        # Determine bearing type from type_id
        type_map = {1: 'deep_groove', 2: 'angular_contact', 3: 'tapered_roller', 4: 'thrust_ball', 5: 'self_aligning', 6: 'cylindrical_roller'}
        bearing_type = type_map.get(bearing.type_id, 'deep_groove')
        defaults = BearingCalculator.get_bearing_type_defaults(bearing_type)
        x0, y0 = defaults['x0'], defaults['y0']

        # Get lubrication factor
        lub_factors = {'grease': 0.7, 'oil_bath': 0.9, 'oil_mist': 0.8, 'oil循环': 1.0}
        lub_factor = lub_factors.get(lubrication.lower(), 0.7)

        # Equivalent load
        e = defaults['e']
        if fa / fr <= e if fr > 0 else False:
            p = fr
        else:
            x, y = 0.56, y0
            p = x * fr + y * fa

        # Basic life
        basic_life = BearingCalculator.calculate_basic_life(
            c=bearing.dynamic_load_rating, p=p, n=speed
        )

        # Modified life
        modified_life = BearingCalculator.calculate_modified_life(
            c=bearing.dynamic_load_rating,
            p=p,
            n=speed,
            reliability=reliability,
            temperature=temperature,
            lubrication_factor=lub_factor
        )

        # Static load check
        static_check = BearingCalculator.check_static_load(
            c0=bearing.static_load_rating,
            fr=fr, fa=fa, x0=x0, y0=y0
        )

        # Stiffness
        stiffness = BearingCalculator.calculate_stiffness(
            bearing_type=bearing_type,
            c=bearing.dynamic_load_rating,
            bore_diameter=bearing.bore_diameter
        )

        return {
            'bearing': bearing.to_dict(),
            'bearing_type': bearing_type,
            'equivalent_load_P': p,
            'basic_life': basic_life,
            'modified_life': modified_life,
            'static_check': static_check,
            'stiffness': stiffness,
            'input': {
                'Fr': fr,
                'Fa': fa,
                'speed': speed,
                'temperature': temperature,
                'lubrication': lubrication,
                'reliability': reliability
            }
        }
