#!/usr/bin/env python3
"""
Debug Chiron retrograde calculations
This script tests if we can calculate Chiron positions and why it might not show retrograde periods
"""

import json
from datetime import datetime
from skyfield.api import load
import numpy as np

def test_chiron_positions():
    """Test if we can get Chiron positions at all"""
    print("Testing Chiron position calculations...")
    
    import os
    original_dir = os.getcwd()
    os.chdir('../data')  # Change to data directory where ephemeris files are
    
    ts = load.timescale()
    
    # Try different ephemeris files
    ephemeris_files = ['de421.bsp', 'de440.bsp', 'de441.bsp']
    
    for eph_file in ephemeris_files:
        print(f"\n--- Testing {eph_file} ---")
        
        try:
            eph = load(eph_file)
            
            # Try to get Chiron
            try:
                chiron = eph[2060]  # Chiron's asteroid number
                earth = eph['earth']
                print(f"✓ Chiron found in {eph_file}")
                
                # Test position calculation for a specific date
                test_date = ts.utc(2024, 9, 4)
                
                # Calculate Chiron's position as seen from Earth
                observation = earth.at(test_date).observe(chiron)
                lat, lon, dist = observation.ecliptic_latlon()
                
                print(f"  Chiron ecliptic longitude on 2024-09-04: {lon.degrees:.2f}°")
                print(f"  Chiron distance from Earth: {dist.au:.2f} AU")
                
                # Now test Earth as seen from Chiron
                observation_reverse = chiron.at(test_date).observe(earth)
                lat_r, lon_r, dist_r = observation_reverse.ecliptic_latlon()
                
                print(f"  Earth ecliptic longitude from Chiron: {lon_r.degrees:.2f}°")
                print(f"  Earth distance from Chiron: {dist_r.au:.2f} AU")
                
                # Test over a short period to see if there's movement
                print(f"  Testing Earth motion from Chiron over 30 days...")
                
                times = ts.utc(2024, 9, range(1, 31))
                observations = chiron.at(times).observe(earth)
                lat_series, lon_series, _ = observations.ecliptic_latlon()
                longitudes = lon_series.degrees
                
                # Check for retrograde motion
                diffs = np.diff(longitudes)
                diffs[diffs > 180] -= 360
                diffs[diffs < -180] += 360
                
                retrograde_days = np.sum(diffs < 0)
                print(f"  Days with retrograde motion in Sept 2024: {retrograde_days}/29")
                
                if retrograde_days > 0:
                    print(f"  ✓ Chiron can see Earth in retrograde!")
                else:
                    print(f"  ⚠ No retrograde motion detected in this period")
                
                return True
                
            except KeyError:
                print(f"✗ Chiron (asteroid 2060) not found in {eph_file}")
                
        except Exception as e:
            print(f"✗ Could not load {eph_file}: {e}")
    
    # Restore original directory
    os.chdir(original_dir)
    return False

def analyze_existing_chiron_data():
    """Check what's in the existing JSON data for Chiron"""
    print(f"\n{'='*60}")
    print("Analyzing existing Chiron data...")
    print(f"{'='*60}")
    
    try:
        with open('../data/retrograde_periods.json', 'r') as f:
            data = json.load(f)
        
        if 'chiron' in data['planets']:
            chiron_data = data['planets']['chiron']
            print(f"Chiron periods found: {chiron_data['count']}")
            print(f"Average per year: {chiron_data['average_per_year']:.3f}")
            
            if chiron_data['periods']:
                print("Chiron retrograde periods:")
                for i, period in enumerate(chiron_data['periods'][:5]):  # Show first 5
                    print(f"  {i+1}. {period['start']} to {period['end']}")
                if len(chiron_data['periods']) > 5:
                    print(f"  ... and {len(chiron_data['periods']) - 5} more")
            else:
                print("No Chiron retrograde periods found")
                
            return len(chiron_data['periods']) > 0
        else:
            print("Chiron not found in JSON data")
            return False
            
    except FileNotFoundError:
        print("JSON data file not found at ../data/retrograde_periods.json")
        return False
    except Exception as e:
        print(f"Error reading JSON data: {e}")
        return False

def compare_chiron_with_other_planets():
    """Compare Chiron's orbital characteristics with other planets"""
    print(f"\n{'='*60}")
    print("Comparing orbital periods...")
    print(f"{'='*60}")
    
    # Approximate orbital periods (years)
    orbital_periods = {
        'mercury': 0.24,
        'venus': 0.62,
        'mars': 1.88,
        'jupiter': 11.86,
        'saturn': 29.46,
        'uranus': 84.01,
        'neptune': 164.8,
        'pluto': 248.1,
        'chiron': 50.4  # Chiron's orbital period
    }
    
    print("Orbital periods (Earth years):")
    for planet, period in orbital_periods.items():
        print(f"  {planet.capitalize()}: {period:.2f} years")
    
    print(f"\nChiron has a {orbital_periods['chiron']:.1f} year orbit.")
    print("This means it moves very slowly, so Earth retrograde periods")
    print("from Chiron's perspective would be very rare and long-lasting.")
    
    # Estimate expected retrograde frequency
    print(f"\nEstimated retrograde characteristics:")
    print("- Fast inner planets (Mercury, Venus): Many short retrograde periods per year")
    print("- Mars: ~1-2 retrograde periods per Earth orbit")
    print("- Outer planets: Fewer, longer retrograde periods")
    print("- Chiron: Very few retrograde periods due to slow motion")

def main():
    print("Chiron Retrograde Debug Tool")
    print("="*60)
    
    # Test if we can calculate Chiron positions
    chiron_available = test_chiron_positions()
    
    # Analyze existing data
    has_data = analyze_existing_chiron_data()
    
    # Educational comparison
    compare_chiron_with_other_planets()
    
    print(f"\n{'='*60}")
    print("DIAGNOSIS")
    print(f"{'='*60}")
    
    if not chiron_available:
        print("❌ ISSUE: Chiron not available in ephemeris files")
        print("   SOLUTION: Try using DE441 which has more asteroids")
    elif not has_data:
        print("❌ ISSUE: Chiron available but no retrograde periods calculated")
        print("   POSSIBLE CAUSES:")
        print("   1. Chiron's slow orbit means very few retrograde events")
        print("   2. Calculation error in the retrograde detection logic")
        print("   3. Time range (1950-2050) may not include Chiron retrograde periods")
    else:
        print("✅ Chiron data looks good!")

if __name__ == "__main__":
    main()