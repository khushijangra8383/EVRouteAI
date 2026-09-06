# physics_engine.py
import math
import pandas as pd
from utils import calculate_haversine_distance

def simulate_ev_journey(geometry, mass, c_d, area, total_cap, initial_soc, wind_speed, is_raining, target_soc):
    """
    Simulates battery discharge over variable terrain micro-segments using pure physics.
    
    SAFETY & BUFFER LOGIC ARCHITECTURE:
    - target_soc: The user's requested battery level upon arrival at the destination.
    - safety_trigger (target_soc + 5%): An operational emergency reserve threshold. If the 
      car hits this buffer mid-journey, it assumes a charging intercept is mandatory.
    - 80% Fast-Charging Limit: Standard EV fast-charging curve profiles throttle performance 
      drastically after 80% to protect battery health. Charging past 80% mid-route is highly 
      inefficient, so the simulator recharges exactly up to this optimal economic ceiling.
    """
    current_soc = float(initial_soc)
    current_energy = (current_soc / 100.0) * total_cap
    safety_trigger = target_soc + 5.0
    
    soc_history = [current_soc]
    distance_history = [0.0]
    stops_found = []
    cumulative_dist = 0.0
    
    # Constants
    g = 9.81
    rho = 1.225
    # Engineering Assumption: Wet roads increase rolling friction drag (c_r) from 0.015 to 0.022
    c_r = 0.015 if not is_raining else 0.022 
    v_car = 16.67  # Approximated urban/semi-urban velocity (~60 km/h)
    powertrain_efficiency = 0.85
    total_kwh_charged_on_way = 0.0
    
    # Pre-calculate overall remaining trip parameters for smart destination tracking
    total_segments = len(geometry) - 1
    
    for i in range(total_segments):
        lon1, lat1, alt1 = geometry[i]
        lon2, lat2, alt2 = geometry[i+1]
        
        seg_dist_km = calculate_haversine_distance(lon1, lat1, lon2, lat2)
        if seg_dist_km == 0:
            continue
            
        seg_dist_m = seg_dist_km * 1000.0
        elevation_delta_m = alt2 - alt1
        slope = math.atan2(elevation_delta_m, seg_dist_m)
        
        # Free Body Diagram Equations
        f_gravity = mass * g * math.sin(slope)
        f_rolling = mass * g * c_r * math.cos(slope)
        f_aerodynamic = 0.5 * rho * c_d * area * (v_car + wind_speed)**2
        
        f_total = f_gravity + f_rolling + f_aerodynamic
        work_joules = f_total * seg_dist_m
        energy_kwh = work_joules / 3600000.0
        
        if energy_kwh > 0:
            actual_kwh_spent = energy_kwh / powertrain_efficiency
        else:
            # Regenerative braking recovery efficiency cap (set to 60%)
            actual_kwh_spent = energy_kwh * 0.60
            
        current_energy -= actual_kwh_spent
        current_energy = max(0.0, min(current_energy, total_cap))
        current_soc = (current_energy / total_cap) * 100.0
        cumulative_dist += seg_dist_km
        
        # Interrupt Loop if battery falls under safety margin
        if current_soc < safety_trigger:
            # Check if we can safely coast directly to the final destination instead of stopping
            approx_remaining_segments = total_segments - i
            estimated_remaining_kwh_needed = (actual_kwh_spent * approx_remaining_segments)
            projected_arrival_energy = current_energy - estimated_remaining_kwh_needed
            projected_arrival_soc = (projected_arrival_energy / total_cap) * 100.0
            
            # If we won't crash past the strict target_soc floor before finishing, bypass charging stop
            if projected_arrival_soc >= target_soc:
                soc_history.append(current_soc)
                distance_history.append(cumulative_dist)
                continue
                
            # Otherwise, initiate optimal mid-route fast charge intercept up to 80% standard ceiling
            energy_needed = (0.80 * total_cap) - current_energy
            total_kwh_charged_on_way += energy_needed
            
            stops_found.append({
                "coord": [lat2, lon2],
                "at_km": cumulative_dist,
                "arrival_soc": current_soc
            })
            current_soc = 80.0
            current_energy = (current_soc / 100.0) * total_cap
            
        soc_history.append(current_soc)
        distance_history.append(cumulative_dist)
        
    net_trip_depletion = ((initial_soc - current_soc) / 100.0) * total_cap
    total_energy_provided = max(0.0, net_trip_depletion + total_kwh_charged_on_way)
    
    df_profile = pd.DataFrame({"Distance (km)": distance_history, "Battery %": soc_history})
    return df_profile, total_energy_provided, stops_found