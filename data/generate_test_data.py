#!/usr/bin/env python3
"""
Generate test data for Earth retrograde periods (just 2024)
This is a quick test before running the full 20,000 year calculation.
"""

import json
from datetime import datetime
from skyfield.api import load
import numpy as np

# Test configuration - just 2024
START_YEAR = 2024
END_YEAR = 2024
OUTPUT_FILE = 'retrograde_periods.json'

# Observers
OBSERVERS = {
    'mercury': 'MERCURY BARYCENTER',
    'venus': 'VENUS BARYCENTER',
    'mars': 'MARS BARYCENTER',
    'jupiter': 'JUPITER BARYCENTER',
    'saturn': 'SATURN BARYCENTER',
    'uranus': 'URANUS BARYCENTER',
    'neptune': 'NEPTUNE BARYCENTER',
    'pluto': 'PLUTO BARYCENTER',
    'chiron': 2060
}

def main():
    print("Generating test data for 2024...")
    
    # Load ephemeris
    ts = load.timescale()
    eph = load('de421.bsp')  # Use DE421 for quick test
    
    earth = eph['earth']
    
    results = {
        'metadata': {
            'generated': datetime.utcnow().isoformat() + 'Z',
            'start_year': START_YEAR,
            'end_year': END_YEAR,
            'version': '1.0',
            'description': 'TEST DATA - Earth retrograde periods as seen from other celestial bodies'
        },
        'planets': {}
    }
    
    # Process each observer
    for observer_name, observer_key in OBSERVERS.items():
        print(f"\nProcessing {observer_name}...")
        
        try:
            # Get observer
            if isinstance(observer_key, int):
                try:
                    observer = eph[observer_key]
                except KeyError:
                    print(f"  {observer_name} not found in DE421")
                    continue
            else:
                observer = eph[observer_key]
            
            # Create daily times for 2024
            start = ts.utc(2024, 1, 1)
            end = ts.utc(2024, 12, 31)
            times = ts.utc(2024, 1, range(1, 367))  # 2024 is leap year
            
            # Calculate Earth's position as seen from observer
            observations = observer.at(times).observe(earth)
            lat, lon, _ = observations.ecliptic_latlon()
            longitudes = lon.degrees
            
            # Find retrograde periods
            diffs = np.diff(longitudes)
            diffs[diffs > 180] -= 360
            diffs[diffs < -180] += 360
            retrograde = diffs < 0
            
            # Extract periods
            periods = []
            in_retro = False
            start_idx = None
            
            for i, is_retro in enumerate(retrograde):
                if is_retro and not in_retro:
                    start_idx = i
                    in_retro = True
                elif not is_retro and in_retro and start_idx is not None:
                    periods.append({
                        'start': times[start_idx].utc_iso(' ').split(' ')[0],
                        'end': times[i].utc_iso(' ').split(' ')[0],
                        'start_jd': float(times[start_idx].tt),
                        'end_jd': float(times[i].tt)
                    })
                    in_retro = False
            
            # Handle case where retrograde continues to year end
            if in_retro and start_idx is not None:
                periods.append({
                    'start': times[start_idx].utc_iso(' ').split(' ')[0],
                    'end': times[-1].utc_iso(' ').split(' ')[0],
                    'start_jd': float(times[start_idx].tt),
                    'end_jd': float(times[-1].tt)
                })
            
            results['planets'][observer_name] = {
                'periods': periods,
                'count': len(periods),
                'average_per_year': len(periods)  # Since it's just 1 year
            }
            
            print(f"  Found {len(periods)} retrograde periods")
            for p in periods:
                print(f"    {p['start']} to {p['end']}")
                
        except Exception as e:
            print(f"  Error: {e}")
            results['planets'][observer_name] = {
                'periods': [],
                'count': 0,
                'average_per_year': 0
            }
    
    # Save results
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nTest data saved to {OUTPUT_FILE}")
    print(f"File size: {len(json.dumps(results)) / 1024:.2f} KB")

if __name__ == "__main__":
    main()