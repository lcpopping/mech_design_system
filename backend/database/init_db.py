"""Initialize database with seed data."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.app import create_app, db
from backend.models import Bearing, BearingType, ServoMotor, ServoMotorType

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()

        # Seed bearing types
        types = [
            BearingType(id=1, name='深沟球轴承', code='6000'),
            BearingType(id=2, name='角接触球轴承', code='7000'),
            BearingType(id=3, name='圆锥滚子轴承', code='30200'),
            BearingType(id=4, name='推力球轴承', code='51000'),
            BearingType(id=5, name='调心球轴承', code='1200'),
            BearingType(id=6, name='圆柱滚子轴承', code='N2000'),
        ]
        for t in types:
            existing = BearingType.query.get(t.id)
            if existing:
                existing.name = t.name
                existing.code = t.code
            else:
                db.session.add(t)

        # Seed deep groove ball bearings (6000 series) - 20 bearings
        deep_groove_bearings = [
            Bearing(model='6000', type_id=1, bore_diameter=10, outer_diameter=26, width=8, dynamic_load_rating=4550, static_load_rating=1960, max_speed=30000, weight=0.019),
            Bearing(model='6001', type_id=1, bore_diameter=12, outer_diameter=28, width=8, dynamic_load_rating=5100, static_load_rating=2370, max_speed=28000, weight=0.022),
            Bearing(model='6002', type_id=1, bore_diameter=15, outer_diameter=32, width=9, dynamic_load_rating=6800, static_load_rating=3100, max_speed=24000, weight=0.030),
            Bearing(model='6003', type_id=1, bore_diameter=17, outer_diameter=35, width=10, dynamic_load_rating=7400, static_load_rating=3500, max_speed=22000, weight=0.040),
            Bearing(model='6004', type_id=1, bore_diameter=20, outer_diameter=42, width=12, dynamic_load_rating=9400, static_load_rating=5050, max_speed=18000, weight=0.069),
            Bearing(model='6005', type_id=1, bore_diameter=25, outer_diameter=47, width=12, dynamic_load_rating=10700, static_load_rating=6250, max_speed=15000, weight=0.082),
            Bearing(model='6006', type_id=1, bore_diameter=30, outer_diameter=55, width=13, dynamic_load_rating=13200, static_load_rating=8300, max_speed=12000, weight=0.119),
            Bearing(model='6007', type_id=1, bore_diameter=35, outer_diameter=62, width=14, dynamic_load_rating=16800, static_load_rating=10900, max_speed=10000, weight=0.160),
            Bearing(model='6008', type_id=1, bore_diameter=40, outer_diameter=68, width=15, dynamic_load_rating=17100, static_load_rating=11800, max_speed=9500, weight=0.190),
            Bearing(model='6009', type_id=1, bore_diameter=45, outer_diameter=75, width=16, dynamic_load_rating=21000, static_load_rating=14800, max_speed=8500, weight=0.240),
            Bearing(model='6010', type_id=1, bore_diameter=50, outer_diameter=80, width=16, dynamic_load_rating=22000, static_load_rating=16200, max_speed=8000, weight=0.280),
            Bearing(model='6011', type_id=1, bore_diameter=55, outer_diameter=90, width=18, dynamic_load_rating=28000, static_load_rating=21200, max_speed=7000, weight=0.380),
            Bearing(model='6012', type_id=1, bore_diameter=60, outer_diameter=95, width=18, dynamic_load_rating=29500, static_load_rating=23200, max_speed=6700, weight=0.410),
            Bearing(model='6013', type_id=1, bore_diameter=65, outer_diameter=100, width=18, dynamic_load_rating=30500, static_load_rating=25000, max_speed=6300, weight=0.440),
            Bearing(model='6014', type_id=1, bore_diameter=70, outer_diameter=110, width=20, dynamic_load_rating=38000, static_load_rating=31000, max_speed=5800, weight=0.600),
            Bearing(model='6015', type_id=1, bore_diameter=75, outer_diameter=115, width=20, dynamic_load_rating=40000, static_load_rating=33500, max_speed=5600, weight=0.640),
            Bearing(model='6016', type_id=1, bore_diameter=80, outer_diameter=125, width=22, dynamic_load_rating=47500, static_load_rating=40000, max_speed=5000, weight=0.850),
            Bearing(model='6017', type_id=1, bore_diameter=85, outer_diameter=130, width=22, dynamic_load_rating=49500, static_load_rating=43000, max_speed=4800, weight=0.890),
            Bearing(model='6018', type_id=1, bore_diameter=90, outer_diameter=140, width=24, dynamic_load_rating=58000, static_load_rating=49500, max_speed=4500, weight=1.100),
            Bearing(model='6019', type_id=1, bore_diameter=95, outer_diameter=145, width=24, dynamic_load_rating=60500, static_load_rating=53000, max_speed=4300, weight=1.150),
        ]

        # Angular contact ball bearings (7000 series) - 15 bearings
        angular_contact_bearings = [
            Bearing(model='7200', type_id=2, bore_diameter=10, outer_diameter=30, width=9, dynamic_load_rating=7100, static_load_rating=4100, max_speed=26000, weight=0.032),
            Bearing(model='7201', type_id=2, bore_diameter=12, outer_diameter=32, width=10, dynamic_load_rating=8150, static_load_rating=4750, max_speed=24000, weight=0.036),
            Bearing(model='7202', type_id=2, bore_diameter=15, outer_diameter=35, width=11, dynamic_load_rating=11200, static_load_rating=6500, max_speed=21000, weight=0.045),
            Bearing(model='7203', type_id=2, bore_diameter=17, outer_diameter=40, width=12, dynamic_load_rating=14500, static_load_rating=8500, max_speed=19000, weight=0.062),
            Bearing(model='7204', type_id=2, bore_diameter=20, outer_diameter=47, width=14, dynamic_load_rating=17700, static_load_rating=11300, max_speed=16000, weight=0.106),
            Bearing(model='7205', type_id=2, bore_diameter=25, outer_diameter=52, width=15, dynamic_load_rating=21200, static_load_rating=14300, max_speed=14000, weight=0.136),
            Bearing(model='7206', type_id=2, bore_diameter=30, outer_diameter=62, width=16, dynamic_load_rating=28000, static_load_rating=20000, max_speed=12000, weight=0.200),
            Bearing(model='7207', type_id=2, bore_diameter=35, outer_diameter=72, width=17, dynamic_load_rating=34500, static_load_rating=25500, max_speed=10000, weight=0.290),
            Bearing(model='7208', type_id=2, bore_diameter=40, outer_diameter=80, width=18, dynamic_load_rating=41500, static_load_rating=32000, max_speed=9000, weight=0.370),
            Bearing(model='7209', type_id=2, bore_diameter=45, outer_diameter=85, width=19, dynamic_load_rating=43500, static_load_rating=34500, max_speed=8500, weight=0.420),
            Bearing(model='7210', type_id=2, bore_diameter=50, outer_diameter=90, width=20, dynamic_load_rating=48000, static_load_rating=39000, max_speed=7800, weight=0.470),
            Bearing(model='7211', type_id=2, bore_diameter=55, outer_diameter=100, width=21, dynamic_load_rating=58000, static_load_rating=47500, max_speed=7000, weight=0.600),
            Bearing(model='7212', type_id=2, bore_diameter=60, outer_diameter=110, width=22, dynamic_load_rating=69500, static_load_rating=57000, max_speed=6300, weight=0.770),
            Bearing(model='7213', type_id=2, bore_diameter=65, outer_diameter=120, width=23, dynamic_load_rating=79500, static_load_rating=67000, max_speed=5800, weight=0.980),
            Bearing(model='7214', type_id=2, bore_diameter=70, outer_diameter=125, width=24, dynamic_load_rating=85000, static_load_rating=73500, max_speed=5600, weight=1.050),
        ]

        # Tapered roller bearings (30200 series) - 15 bearings
        tapered_roller_bearings = [
            Bearing(model='30202', type_id=3, bore_diameter=15, outer_diameter=42, width=13, dynamic_load_rating=22500, static_load_rating=21500, max_speed=14000, weight=0.090),
            Bearing(model='30203', type_id=3, bore_diameter=17, outer_diameter=47, width=14, dynamic_load_rating=27000, static_load_rating=27500, max_speed=12000, weight=0.115),
            Bearing(model='30204', type_id=3, bore_diameter=20, outer_diameter=47, width=14, dynamic_load_rating=33000, static_load_rating=33000, max_speed=11000, weight=0.115),
            Bearing(model='30205', type_id=3, bore_diameter=25, outer_diameter=52, width=15, dynamic_load_rating=37000, static_load_rating=38000, max_speed=10000, weight=0.144),
            Bearing(model='30206', type_id=3, bore_diameter=30, outer_diameter=62, width=17, dynamic_load_rating=48000, static_load_rating=51000, max_speed=9000, weight=0.221),
            Bearing(model='30207', type_id=3, bore_diameter=35, outer_diameter=72, width=18, dynamic_load_rating=60000, static_load_rating=67000, max_speed=8000, weight=0.318),
            Bearing(model='30208', type_id=3, bore_diameter=40, outer_diameter=80, width=20, dynamic_load_rating=73500, static_load_rating=83000, max_speed=7000, weight=0.420),
            Bearing(model='30209', type_id=3, bore_diameter=45, outer_diameter=85, width=21, dynamic_load_rating=78000, static_load_rating=91500, max_speed=6500, weight=0.480),
            Bearing(model='30210', type_id=3, bore_diameter=50, outer_diameter=90, width=22, dynamic_load_rating=85000, static_load_rating=102000, max_speed=6000, weight=0.540),
            Bearing(model='30211', type_id=3, bore_diameter=55, outer_diameter=100, width=23, dynamic_load_rating=102000, static_load_rating=125000, max_speed=5500, weight=0.680),
            Bearing(model='30212', type_id=3, bore_diameter=60, outer_diameter=110, width=24, dynamic_load_rating=118000, static_load_rating=145000, max_speed=5000, weight=0.840),
            Bearing(model='30213', type_id=3, bore_diameter=65, outer_diameter=120, width=25, dynamic_load_rating=135000, static_load_rating=170000, max_speed=4600, weight=1.040),
            Bearing(model='30214', type_id=3, bore_diameter=70, outer_diameter=125, width=26, dynamic_load_rating=145000, static_load_rating=185000, max_speed=4400, weight=1.130),
            Bearing(model='30215', type_id=3, bore_diameter=75, outer_diameter=130, width=27, dynamic_load_rating=155000, static_load_rating=200000, max_speed=4200, weight=1.220),
        ]

        # Thrust ball bearings (51000 series) - 12 bearings
        thrust_ball_bearings = [
            Bearing(model='51100', type_id=4, bore_diameter=10, outer_diameter=26, width=11, dynamic_load_rating=12700, static_load_rating=21300, max_speed=10000, weight=0.026),
            Bearing(model='51101', type_id=4, bore_diameter=12, outer_diameter=28, width=11, dynamic_load_rating=13500, static_load_rating=23500, max_speed=9500, weight=0.030),
            Bearing(model='51102', type_id=4, bore_diameter=15, outer_diameter=32, width=12, dynamic_load_rating=16800, static_load_rating=31500, max_speed=8500, weight=0.043),
            Bearing(model='51103', type_id=4, bore_diameter=17, outer_diameter=35, width=12, dynamic_load_rating=17800, static_load_rating=35500, max_speed=8000, weight=0.050),
            Bearing(model='51104', type_id=4, bore_diameter=20, outer_diameter=40, width=14, dynamic_load_rating=23800, static_load_rating=48500, max_speed=7000, weight=0.073),
            Bearing(model='51105', type_id=4, bore_diameter=25, outer_diameter=47, width=15, dynamic_load_rating=28500, static_load_rating=62500, max_speed=6000, weight=0.110),
            Bearing(model='51106', type_id=4, bore_diameter=30, outer_diameter=52, width=16, dynamic_load_rating=31000, static_load_rating=73500, max_speed=5600, weight=0.130),
            Bearing(model='51107', type_id=4, bore_diameter=35, outer_diameter=62, width=18, dynamic_load_rating=38500, static_load_rating=97500, max_speed=4800, weight=0.200),
            Bearing(model='51108', type_id=4, bore_diameter=40, outer_diameter=68, width=19, dynamic_load_rating=43000, static_load_rating=112000, max_speed=4500, weight=0.240),
            Bearing(model='51109', type_id=4, bore_diameter=45, outer_diameter=73, width=20, dynamic_load_rating=46500, static_load_rating=128000, max_speed=4200, weight=0.270),
            Bearing(model='51110', type_id=4, bore_diameter=50, outer_diameter=78, width=22, dynamic_load_rating=56000, static_load_rating=158000, max_speed=3800, weight=0.340),
            Bearing(model='51111', type_id=4, bore_diameter=55, outer_diameter=90, width=25, dynamic_load_rating=70500, static_load_rating=215000, max_speed=3400, weight=0.530),
        ]

        # Self-aligning ball bearings (1200 series) - 12 bearings
        self_aligning_bearings = [
            Bearing(model='1200', type_id=5, bore_diameter=10, outer_diameter=30, width=9, dynamic_load_rating=5500, static_load_rating=1300, max_speed=26000, weight=0.030),
            Bearing(model='1201', type_id=5, bore_diameter=12, outer_diameter=32, width=10, dynamic_load_rating=6800, static_load_rating=1650, max_speed=24000, weight=0.038),
            Bearing(model='1202', type_id=5, bore_diameter=15, outer_diameter=35, width=11, dynamic_load_rating=7400, static_load_rating=1900, max_speed=22000, weight=0.045),
            Bearing(model='1203', type_id=5, bore_diameter=17, outer_diameter=40, width=12, dynamic_load_rating=9500, static_load_rating=2600, max_speed=19000, weight=0.062),
            Bearing(model='1204', type_id=5, bore_diameter=20, outer_diameter=47, width=14, dynamic_load_rating=12700, static_load_rating=3700, max_speed=17000, weight=0.100),
            Bearing(model='1205', type_id=5, bore_diameter=25, outer_diameter=52, width=15, dynamic_load_rating=14000, static_load_rating=4400, max_speed=15000, weight=0.120),
            Bearing(model='1206', type_id=5, bore_diameter=30, outer_diameter=62, width=16, dynamic_load_rating=15600, static_load_rating=5400, max_speed=13000, weight=0.190),
            Bearing(model='1207', type_id=5, bore_diameter=35, outer_diameter=72, width=17, dynamic_load_rating=21600, static_load_rating=7300, max_speed=11000, weight=0.290),
            Bearing(model='1208', type_id=5, bore_diameter=40, outer_diameter=80, width=18, dynamic_load_rating=22400, static_load_rating=8150, max_speed=10000, weight=0.370),
            Bearing(model='1209', type_id=5, bore_diameter=45, outer_diameter=85, width=19, dynamic_load_rating=24000, static_load_rating=9150, max_speed=9500, weight=0.420),
            Bearing(model='1210', type_id=5, bore_diameter=50, outer_diameter=90, width=20, dynamic_load_rating=26500, static_load_rating=10400, max_speed=9000, weight=0.480),
            Bearing(model='1211', type_id=5, bore_diameter=55, outer_diameter=100, width=21, dynamic_load_rating=30000, static_load_rating=11900, max_speed=8200, weight=0.640),
        ]

        # Cylindrical roller bearings (N2000 series) - 12 bearings
        cylindrical_roller_bearings = [
            Bearing(model='N203', type_id=6, bore_diameter=17, outer_diameter=40, width=12, dynamic_load_rating=21000, static_load_rating=17500, max_speed=18000, weight=0.062),
            Bearing(model='N204', type_id=6, bore_diameter=20, outer_diameter=47, width=14, dynamic_load_rating=28000, static_load_rating=24000, max_speed=16000, weight=0.106),
            Bearing(model='N205', type_id=6, bore_diameter=25, outer_diameter=52, width=15, dynamic_load_rating=33000, static_load_rating=30000, max_speed=14000, weight=0.132),
            Bearing(model='N206', type_id=6, bore_diameter=30, outer_diameter=62, width=16, dynamic_load_rating=42500, static_load_rating=40000, max_speed=12000, weight=0.205),
            Bearing(model='N207', type_id=6, bore_diameter=35, outer_diameter=72, width=17, dynamic_load_rating=52000, static_load_rating=50000, max_speed=10000, weight=0.290),
            Bearing(model='N208', type_id=6, bore_diameter=40, outer_diameter=80, width=18, dynamic_load_rating=58500, static_load_rating=57500, max_speed=9500, weight=0.370),
            Bearing(model='N209', type_id=6, bore_diameter=45, outer_diameter=85, width=19, dynamic_load_rating=62500, static_load_rating=63000, max_speed=9000, weight=0.420),
            Bearing(model='N210', type_id=6, bore_diameter=50, outer_diameter=90, width=20, dynamic_load_rating=69500, static_load_rating=72000, max_speed=8500, weight=0.470),
            Bearing(model='N211', type_id=6, bore_diameter=55, outer_diameter=100, width=21, dynamic_load_rating=83500, static_load_rating=88000, max_speed=7800, weight=0.610),
            Bearing(model='N212', type_id=6, bore_diameter=60, outer_diameter=110, width=22, dynamic_load_rating=95000, static_load_rating=102000, max_speed=7200, weight=0.770),
            Bearing(model='N213', type_id=6, bore_diameter=65, outer_diameter=120, width=23, dynamic_load_rating=108000, static_load_rating=118000, max_speed=6700, weight=0.960),
            Bearing(model='N214', type_id=6, bore_diameter=70, outer_diameter=125, width=24, dynamic_load_rating=115000, static_load_rating=128000, max_speed=6300, weight=1.050),
        ]

        all_bearings = (deep_groove_bearings + angular_contact_bearings + tapered_roller_bearings +
                       thrust_ball_bearings + self_aligning_bearings + cylindrical_roller_bearings)

        for b in all_bearings:
            existing = Bearing.query.filter_by(model=b.model).first()
            if existing:
                for key in ['bore_diameter', 'outer_diameter', 'width', 'dynamic_load_rating',
                           'static_load_rating', 'max_speed', 'weight', 'type_id']:
                    setattr(existing, key, getattr(b, key))
            else:
                db.session.add(b)

        db.session.commit()
        print(f'Database initialized successfully! Total bearings: {len(all_bearings)}')

        # Seed servo motor types
        servo_types = [
            ServoMotorType(id=1, name='交流伺服电机', code='AC_SERVO', description='交流伺服电机'),
        ]
        for t in servo_types:
            existing = ServoMotorType.query.get(t.id)
            if existing:
                existing.name = t.name
                existing.code = t.code
                existing.description = t.description
            else:
                db.session.add(t)

        # Seed servo motors - common sizes from 100W to 5kW
        servo_motors = [
            ServoMotor(model='SG-100', type_id=1, power_w=100, rated_torque_nm=0.32, max_torque_nm=0.95, rated_speed_rpm=3000, max_speed_rpm=5000, inertia_kgm2=0.026, voltage_v=220, rated_current_a=0.6, frame_size='40', shaft_diameter=8, weight_kg=0.3, brake=False),
            ServoMotor(model='SG-200', type_id=1, power_w=200, rated_torque_nm=0.64, max_torque_nm=1.9, rated_speed_rpm=3000, max_speed_rpm=5000, inertia_kgm2=0.05, voltage_v=220, rated_current_a=1.2, frame_size='60', shaft_diameter=11, weight_kg=0.5, brake=False),
            ServoMotor(model='SG-400', type_id=1, power_w=400, rated_torque_nm=1.27, max_torque_nm=3.8, rated_speed_rpm=3000, max_speed_rpm=5000, inertia_kgm2=0.17, voltage_v=220, rated_current_a=2.3, frame_size='60', shaft_diameter=14, weight_kg=0.8, brake=False),
            ServoMotor(model='SG-750', type_id=1, power_w=750, rated_torque_nm=2.4, max_torque_nm=7.2, rated_speed_rpm=3000, max_speed_rpm=5000, inertia_kgm2=0.35, voltage_v=220, rated_current_a=4.0, frame_size='80', shaft_diameter=19, weight_kg=1.5, brake=False),
            ServoMotor(model='SG-1000', type_id=1, power_w=1000, rated_torque_nm=3.18, max_torque_nm=9.5, rated_speed_rpm=3000, max_speed_rpm=5000, inertia_kgm2=0.51, voltage_v=220, rated_current_a=5.0, frame_size='80', shaft_diameter=22, weight_kg=2.0, brake=False),
            ServoMotor(model='SG-1500', type_id=1, power_w=1500, rated_torque_nm=4.77, max_torque_nm=14.3, rated_speed_rpm=3000, max_speed_rpm=5000, inertia_kgm2=0.78, voltage_v=220, rated_current_a=7.5, frame_size='100', shaft_diameter=22, weight_kg=2.5, brake=False),
            ServoMotor(model='SG-2000', type_id=1, power_w=2000, rated_torque_nm=6.37, max_torque_nm=19.1, rated_speed_rpm=3000, max_speed_rpm=5000, inertia_kgm2=1.15, voltage_v=220, rated_current_a=10.0, frame_size='100', shaft_diameter=25, weight_kg=3.0, brake=False),
            ServoMotor(model='SG-3000', type_id=1, power_w=3000, rated_torque_nm=9.55, max_torque_nm=28.6, rated_speed_rpm=3000, max_speed_rpm=5000, inertia_kgm2=2.0, voltage_v=220, rated_current_a=14.0, frame_size='130', shaft_diameter=32, weight_kg=5.0, brake=False),
            ServoMotor(model='SG-5000', type_id=1, power_w=5000, rated_torque_nm=15.9, max_torque_nm=47.7, rated_speed_rpm=2000, max_speed_rpm=4000, inertia_kgm2=3.5, voltage_v=220, rated_current_a=22.0, frame_size='130', shaft_diameter=35, weight_kg=7.0, brake=False),
        ]

        for m in servo_motors:
            existing = ServoMotor.query.filter_by(model=m.model).first()
            if existing:
                for key in ['power_w', 'rated_torque_nm', 'max_torque_nm', 'rated_speed_rpm', 'max_speed_rpm', 'inertia_kgm2', 'voltage_v', 'rated_current_a', 'frame_size', 'shaft_diameter', 'weight_kg', 'brake', 'type_id']:
                    setattr(existing, key, getattr(m, key))
            else:
                db.session.add(m)

        db.session.commit()
        print(f'Servo motor data seeded successfully! Total servo motors: {len(servo_motors)}')

if __name__ == '__main__':
    init_db()