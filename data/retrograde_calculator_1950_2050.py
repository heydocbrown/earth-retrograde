#!/usr/bin/env python3
"""
Earth Retrograde Calculator - 100 Year Version (1950-2050)
Calculates when Earth is in retrograde as seen from other planets.
"""

import json
import os
from datetime import datetime
from skyfield.api import load
import numpy as np
from tqdm import tqdm

# Configuration - Just 100 years for faster generation
START_YEAR = 1950
END_YEAR = 2050
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
    'chiron': 2060  # Available in SB441-N16 asteroid ephemeris
}

class EarthRetrogradeFinder:
    def __init__(self):
        print("Initializing Earth Retrograde Finder...")
        self.ts = load.timescale()
        
        # Check if ephemeris files exist before downloading
        loader = load
        if os.path.exists(loader.path_to('de421.bsp')):
            print("DE421 already downloaded, using existing file...")
        else:
            print("Downloading DE421 (smaller ephemeris for 1900-2050)...")
        
        # Load main ephemeris
        self.eph = load('de421.bsp')
        
        # Try to load asteroid ephemeris for Chiron
        asteroid_files_to_try = [
            'sb441-n16.bsp',  # Original attempt
            'sb441.bsp',      # Without -n16
            'asteroids.bsp'   # Generic name
        ]
        
        self.asteroid_eph = None
        for ast_file in asteroid_files_to_try:
            try:
                if os.path.exists(loader.path_to(ast_file)):
                    print(f"{ast_file} already downloaded, using existing file...")
                else:
                    print(f"Trying to download {ast_file}...")
                
                self.asteroid_eph = load(ast_file)
                print(f"Successfully loaded {ast_file}")
                break
            except Exception as e:
                print(f"Failed to load {ast_file}: {e}")
                continue
        
        if not self.asteroid_eph:
            print("WARNING: No asteroid ephemeris available - Chiron will be skipped")
        print("Ephemeris files loaded successfully!")
    
    def is_earth_retrograde(self, ecliptic_longitudes):
        """Check if Earth is retrograde based on ecliptic longitude changes."""
        diffs = np.diff(ecliptic_longitudes)
        diffs[diffs > 180] -= 360
        diffs[diffs < -180] += 360
        return diffs < 0
    
    def find_earth_retrograde_periods(self, observer_name, observer_key):
        """Find all periods when Earth appears retrograde from a given observer."""
        print(f"\nCalculating Earth retrograde from {observer_name}...")
        periods = []
        
        # Process in 10-year chunks
        chunk_years = 10
        
        for chunk_start in tqdm(range(START_YEAR, END_YEAR, chunk_years)):
            chunk_end = min(chunk_start + chunk_years, END_YEAR)
            
            # Create time array
            start_date = self.ts.utc(chunk_start, 1, 1)
            end_date = self.ts.utc(chunk_end, 12, 31)
            
            # Daily resolution
            num_days = int((end_date.tt - start_date.tt))
            times = self.ts.tt_jd(np.linspace(start_date.tt, end_date.tt, num_days))
            
            # Get objects - use appropriate ephemeris
            if observer_name == 'chiron':
                # Chiron is in the asteroid ephemeris
                if not self.asteroid_eph:
                    print(f"  Skipping {observer_name} - no asteroid ephemeris available")
                    continue
                earth = self.asteroid_eph['earth']
                observer = self.asteroid_eph[observer_key]
            else:
                # Planets are in the main ephemeris
                earth = self.eph['earth']
                try:
                    if isinstance(observer_key, int):
                        observer = self.eph[observer_key]
                    else:
                        observer = self.eph[observer_key]
                except KeyError:
                    print(f"  Warning: {observer_name} not found in main ephemeris")
                    continue
            
            # Calculate positions
            try:
                observations = observer.at(times).observe(earth)
                lat, lon, _ = observations.ecliptic_latlon()
                earth_longitudes = lon.degrees
                
                # Find retrograde periods
                retrograde = self.is_earth_retrograde(earth_longitudes)
                
                # Extract periods
                in_retrograde = False
                start_idx = None
                
                for i, is_retro in enumerate(retrograde):
                    if is_retro and not in_retrograde:
                        start_idx = i
                        in_retrograde = True
                    elif not is_retro and in_retrograde:
                        if start_idx is not None:
                            start_time = times[start_idx]
                            end_time = times[i]
                            
                            periods.append({
                                'start': start_time.utc_iso(' ').split(' ')[0],
                                'end': end_time.utc_iso(' ').split(' ')[0],
                                'start_jd': float(start_time.tt),
                                'end_jd': float(end_time.tt)
                            })
                        in_retrograde = False
                
            except Exception as e:
                print(f"  Error processing {observer_name}: {e}")
                continue
        
        return periods
    
    def calculate_all_retrogrades(self):
        """Calculate Earth's retrograde periods from all observers."""
        results = {
            'metadata': {
                'generated': datetime.utcnow().isoformat() + 'Z',
                'start_year': START_YEAR,
                'end_year': END_YEAR,
                'total_years': END_YEAR - START_YEAR,
                'version': '1.0',
                'description': 'Earth retrograde periods as observed from other celestial bodies'
            },
            'planets': {}
        }
        
        # Calculate for each observer
        for observer_name, observer_key in OBSERVERS.items():
            periods = self.find_earth_retrograde_periods(observer_name, observer_key)
            results['planets'][observer_name] = {
                'periods': periods,
                'count': len(periods),
                'average_per_year': len(periods) / (END_YEAR - START_YEAR) if periods else 0
            }
            print(f"  {observer_name}: {len(periods)} retrograde periods found")
        
        return results
    
    def save_results(self, results):
        """Save results as JSON."""
        print(f"\nSaving results to {OUTPUT_FILE}...")
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        file_size = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
        print(f"File size: {file_size:.2f} MB")

def main():
    """Main execution function."""
    print("=" * 60)
    print("Earth Retrograde Calculator (1950-2050)")
    print("=" * 60)
    
    start_time = datetime.now()
    
    # Create finder instance
    finder = EarthRetrogradeFinder()
    
    # Calculate all retrogrades
    results = finder.calculate_all_retrogrades()
    
    # Save results
    finder.save_results(results)
    
    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\nComplete! Generated in {duration:.1f} seconds")
    print(f"Results saved to: {OUTPUT_FILE}")
    
    print("\nSummary:")
    total_periods = sum(planet['count'] for planet in results['planets'].values())
    print(f"Total Earth retrograde periods: {total_periods:,}")
    print(f"Years covered: {END_YEAR - START_YEAR}")
    
    print("\nEarth retrograde periods per observer:")
    for planet, data in results['planets'].items():
        print(f"  From {planet.capitalize()}: {data['count']} "
              f"(~{data['average_per_year']:.2f} per year)")

if __name__ == "__main__":
    main()