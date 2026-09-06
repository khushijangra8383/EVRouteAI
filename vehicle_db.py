# vehicle_db.py

POPULAR_INDIAN_EVS = {
    "Tata Nexon EV (Creative 45)": {"battery_capacity": 45.0, "weight": 1450, "drag_coeff": 0.29, "frontal_area": 2.2},
    "Tata Nexon EV (Medium Range)": {"battery_capacity": 30.0, "weight": 1330, "drag_coeff": 0.29, "frontal_area": 2.2},
    "Tata Punch EV (Long Range)": {"battery_capacity": 40.0, "weight": 1360, "drag_coeff": 0.32, "frontal_area": 2.3},
    "Tata Punch EV (Medium Range)": {"battery_capacity": 30.0, "weight": 1240, "drag_coeff": 0.32, "frontal_area": 2.3},
    "Tata Curvv EV (55 kWh)": {"battery_capacity": 55.0, "weight": 1600, "drag_coeff": 0.28, "frontal_area": 2.3},
    "Tata Tiago EV (Long Range)": {"battery_capacity": 24.0, "weight": 1150, "drag_coeff": 0.33, "frontal_area": 2.1},
    "Tata Tigor EV": {"battery_capacity": 26.0, "weight": 1235, "drag_coeff": 0.33, "frontal_area": 2.1},
    "MG ZS EV": {"battery_capacity": 50.3, "weight": 1600, "drag_coeff": 0.32, "frontal_area": 2.4},
    "MG Windsor EV": {"battery_capacity": 38.0, "weight": 1550, "drag_coeff": 0.30, "frontal_area": 2.4},
    "MG Comet EV": {"battery_capacity": 17.3, "weight": 815, "drag_coeff": 0.39, "frontal_area": 2.0},
    "Mahindra XUV400": {"battery_capacity": 39.4, "weight": 1580, "drag_coeff": 0.33, "frontal_area": 2.4},
    "Mahindra XUV 3XO EV": {"battery_capacity": 39.4, "weight": 1520, "drag_coeff": 0.33, "frontal_area": 2.4},
    "BYD Atto 3 (Extended)": {"battery_capacity": 60.5, "weight": 1750, "drag_coeff": 0.29, "frontal_area": 2.5},
    "BYD Seal (Dynamic)": {"battery_capacity": 61.4, "weight": 1920, "drag_coeff": 0.22, "frontal_area": 2.2},
    "BYD e6 (MPV)": {"battery_capacity": 71.7, "weight": 1930, "drag_coeff": 0.29, "frontal_area": 2.6},
    "Hyundai Ioniq 5": {"battery_capacity": 72.6, "weight": 2000, "drag_coeff": 0.28, "frontal_area": 2.6},
    "Hyundai Kona Electric": {"battery_capacity": 39.2, "weight": 1535, "drag_coeff": 0.29, "frontal_area": 2.3},
    "Kia EV6 (GT-Line)": {"battery_capacity": 77.4, "weight": 2100, "drag_coeff": 0.28, "frontal_area": 2.5},
    "Volvo XC40 Recharge": {"battery_capacity": 78.0, "weight": 2180, "drag_coeff": 0.32, "frontal_area": 2.6},
    "BMW i4 (eDrive40)": {"battery_capacity": 80.7, "weight": 2050, "drag_coeff": 0.24, "frontal_area": 2.3}
}