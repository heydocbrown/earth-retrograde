#!/usr/bin/env python3
"""
Planetary Retrograde Calculator
Calculates all planetary retrograde periods from year -10,000 to +10,000
using JPL's DE440 (for 1550-2650) and DE441 (for extended range).

Requirements:
    pip install skyfield numpy tqdm

Note: This script will download ephemeris files on first run:
    - DE440: ~114 MB (for years 1550-2650)
    - DE441: ~3.2 GB (for full range)

Output: JSON file with retrograde periods for all planets
"""

import json
import gzip
from datetime import datetime
from skyfield.api import load
from skyfield.timelib import Time
import numpy as np
from tqdm import tqdm
import os

# Configuration
START_YEAR = -10000
END_YEAR = 10000
OUTPUT_FILE = 'retrograde_periods.json.gz'  # Compressed output

# DE440 coverage for higher accuracy
DE440_START = 1550
DE440_END = 2650

# Planet names we want to check
PLANETS = {
    'mercury': 'MERCURY BARYCENTER',
    'venus': 'VENUS BARYCENTER',
    'mars': 'MARS BARYCENTER',
    'jupiter': 'JUPITER BARYCENTER',
    'saturn': 'SATURN BARYCENTER',
    'uranus': 'URANUS BARYCENTER',
    'neptune': 'NEPTUNE BARYCENTER',
    'pluto': 'PLUTO BARYCENTER'
}

# Optional: Include Chiron
INCLUDE_CHIRON = True
if INCLUDE_CHIRON:
    PLANETS['chiron'] = 2060  # Chiron's asteroid number


class RetrogradeFinder:
    def __init__(self):
        print("Loading ephemeris files...")
        self.ts = load.timescale()
        
        # Download ephemeris files if needed
        print("Loading DE440 (for years 1550-2650)...")
        self.eph_440 = load('de440.bsp')
        
        print("Loading DE441 (for full range)...")
        self.eph_441 = load('de441.bsp')
        
        # Earth objects from both ephemerides
        self.earth_440 = self.eph_440['earth']
        self.earth_441 = self.eph_441['earth']
        
        print("Ephemeris files loaded successfully!")
    
    def get_ephemeris_and_earth(self, year):
        """Select appropriate ephemeris based on year."""
        if DE440_START <= year <= DE440_END:
            return self.eph_440, self.earth_440
        else:
            return self.eph_441, self.earth_441
    
    def is_retrograde(self, ecliptic_longitudes):
        """
        Check if planet is retrograde based on ecliptic longitude changes.
        Returns boolean array where True = retrograde.
        """
        # Calculate daily changes in longitude
        diffs = np.diff(ecliptic_longitudes)
        
        # Handle wraparound at 360 degrees
        diffs[diffs > 180] -= 360
        diffs[diffs < -180] += 360
        
        # Retrograde when longitude is decreasing
        return diffs < 0
    
    def find_retrograde_periods(self, planet_name, planet_key):
        """Find all retrograde periods for a planet across the full time range."""
        print(f"\nCalculating {planet_name} retrograde periods...")
        periods = []
        
        # Process in chunks to manage memory
        chunk_years = 100
        
        for chunk_start in tqdm(range(START_YEAR, END_YEAR, chunk_years)):
            chunk_end = min(chunk_start + chunk_years, END_YEAR)
            
            # Create time array for this chunk
            start_date = self.ts.utc(chunk_start, 1, 1)
            end_date = self.ts.utc(chunk_end, 12, 31)
            
            # Daily resolution
            num_days = int((end_date.tt - start_date.tt) * 365.25)
            times = self.ts.tt_jd(np.linspace(start_date.tt, end_date.tt, num_days))
            
            # Get appropriate ephemeris for this chunk
            mid_year = (chunk_start + chunk_end) // 2
            eph, earth = self.get_ephemeris_and_earth(mid_year)
            
            # Get planet object
            try:
                if isinstance(planet_key, int):  # Asteroid number
                    planet = eph[planet_key]
                else:
                    planet = eph[planet_key]
            except KeyError:
                # Planet might not be in this ephemeris, try the other one
                other_eph = self.eph_441 if eph == self.eph_440 else self.eph_440
                try:
                    if isinstance(planet_key, int):
                        planet = other_eph[planet_key]
                    else:
                        planet = other_eph[planet_key]
                except KeyError:
                    print(f"Warning: {planet_name} not found in ephemerides")
                    continue
            
            # Calculate positions
            try:
                # Observe planet from Earth
                observations = earth.at(times).observe(planet)
                
                # Get ecliptic coordinates
                lat, lon, _ = observations.ecliptic_latlon()
                longitudes = lon.degrees
                
                # Find retrograde periods
                retrograde = self.is_retrograde(longitudes)
                
                # Extract periods (find transitions)
                in_retrograde = False
                start_idx = None
                
                for i, is_retro in enumerate(retrograde):
                    if is_retro and not in_retrograde:
                        # Starting retrograde
                        start_idx = i
                        in_retrograde = True
                    elif not is_retro and in_retrograde:
                        # Ending retrograde
                        if start_idx is not None:
                            # Convert to dates
                            start_time = times[start_idx]
                            end_time = times[i]
                            
                            # Store as ISO dates for readability
                            periods.append({
                                'start': start_time.utc_iso(' ').split(' ')[0],
                                'end': end_time.utc_iso(' ').split(' ')[0],
                                'start_jd': float(start_time.tt),  # Julian date for precision
                                'end_jd': float(end_time.tt)
                            })
                        in_retrograde = False
                
                # Handle case where retrograde continues past chunk
                if in_retrograde and start_idx is not None:
                    # Will be picked up in next chunk
                    pass
                    
            except Exception as e:
                print(f"Error processing {planet_name} in years {chunk_start}-{chunk_end}: {e}")
                continue
        
        return periods
    
    def calculate_all_retrogrades(self):
        """Calculate retrograde periods for all planets."""
        results = {
            'metadata': {
                'generated': datetime.utcnow().isoformat() + 'Z',
                'start_year': START_YEAR,
                'end_year': END_YEAR,
                'ephemerides': {
                    'de440': {'start': DE440_START, 'end': DE440_END},
                    'de441': {'start': START_YEAR, 'end': END_YEAR}
                },
                'total_years': END_YEAR - START_YEAR,
                'version': '1.0'
            },
            'planets': {}
        }
        
        # Calculate for each planet
        for planet_name, planet_key in PLANETS.items():
            periods = self.find_retrograde_periods(planet_name, planet_key)
            results['planets'][planet_name] = {
                'periods': periods,
                'count': len(periods),
                'average_per_year': len(periods) / (END_YEAR - START_YEAR) if periods else 0
            }
            print(f"{planet_name}: {len(periods)} retrograde periods found")
        
        return results
    
    def save_results(self, results):
        """Save results as compressed JSON."""
        print(f"\nSaving results to {OUTPUT_FILE}...")
        
        # Save compressed
        with gzip.open(OUTPUT_FILE, 'wt', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        # Also save uncompressed for easy viewing
        uncompressed_file = OUTPUT_FILE.replace('.gz', '')
        with open(uncompressed_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        # Report file sizes
        compressed_size = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
        uncompressed_size = os.path.getsize(uncompressed_file) / (1024 * 1024)
        
        print(f"Compressed size: {compressed_size:.2f} MB")
        print(f"Uncompressed size: {uncompressed_size:.2f} MB")
        print(f"Compression ratio: {uncompressed_size/compressed_size:.1f}x")


def main():
    """Main execution function."""
    print("=" * 60)
    print("Planetary Retrograde Calculator")
    print(f"Calculating retrogrades from year {START_YEAR} to {END_YEAR}")
    print("=" * 60)
    
    # Create finder instance
    finder = RetrogradeFinder()
    
    # Calculate all retrogrades
    results = finder.calculate_all_retrogrades()
    
    # Save results
    finder.save_results(results)
    
    print("\nComplete! Results saved to:")
    print(f"  - {OUTPUT_FILE} (compressed)")
    print(f"  - {OUTPUT_FILE.replace('.gz', '')} (uncompressed)")
    
    # Print summary statistics
    print("\nSummary:")
    total_periods = sum(planet['count'] for planet in results['planets'].values())
    print(f"Total retrograde periods found: {total_periods:,}")
    print(f"Years covered: {END_YEAR - START_YEAR:,}")
    
    print("\nPeriods per planet:")
    for planet, data in results['planets'].items():
        print(f"  {planet.capitalize()}: {data['count']:,} "
              f"(~{data['average_per_year']:.2f} per year)")


if __name__ == "__main__":
    main()
