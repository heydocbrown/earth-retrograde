#!/usr/bin/env python3
"""
Check what celestial bodies are available in different ephemeris files
"""

from skyfield.api import load
import os

def check_ephemeris(eph_file, name):
    """Check what bodies are available in an ephemeris file"""
    print(f"\n{'='*60}")
    print(f"Checking {name}")
    print(f"File: {eph_file}")
    print(f"{'='*60}")
    
    try:
        # Set up loader to look in data folder
        import os
        original_dir = os.getcwd()
        os.chdir('../data')  # Change to data directory
        
        # Check if file exists
        loader = load
        file_path = loader.path_to(eph_file)
        if os.path.exists(file_path):
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            print(f"File size: {size_mb:.1f} MB")
            print(f"File location: {file_path}")
        else:
            print("File not found in data folder - will be downloaded if used")
        
        # Load ephemeris
        eph = load(eph_file)
        
        # Get all available bodies
        print(f"\nAll available bodies in {name}:")
        print("-" * 40)
        
        # Try common planet names
        planets_to_check = [
            'mercury barycenter', 'MERCURY BARYCENTER',
            'venus barycenter', 'VENUS BARYCENTER', 
            'mars barycenter', 'MARS BARYCENTER',
            'jupiter barycenter', 'JUPITER BARYCENTER',
            'saturn barycenter', 'SATURN BARYCENTER',
            'uranus barycenter', 'URANUS BARYCENTER',
            'neptune barycenter', 'NEPTUNE BARYCENTER',
            'pluto barycenter', 'PLUTO BARYCENTER',
            'earth', 'EARTH'
        ]
        
        # Check asteroids with names
        asteroids_to_check = {
            2060: "Chiron",
            1: "Ceres", 
            4: "Vesta"
        }
        
        found_planets = []
        for planet in planets_to_check:
            try:
                body = eph[planet]
                found_planets.append(planet)
                print(f"  ✓ {planet}")
            except KeyError:
                pass
        
        print(f"\nAsteroids in {name}:")
        print("-" * 40)
        found_asteroids = []
        for asteroid_num, asteroid_name in asteroids_to_check.items():
            try:
                body = eph[asteroid_num]
                found_asteroids.append(asteroid_num)
                print(f"  ✓ {asteroid_num} {asteroid_name} (found)")
            except KeyError:
                print(f"  ✗ {asteroid_num} {asteroid_name} (not found)")
        
        # Try to get a complete listing
        print(f"\nTrying to enumerate all bodies...")
        try:
            # This might not work for all ephemeris files
            bodies = list(eph.names())
            print(f"Total bodies available: {len(bodies)}")
            
            # Show first 20 bodies
            print("\nFirst 20 bodies:")
            for i, body in enumerate(bodies[:20]):
                print(f"  {body}")
            if len(bodies) > 20:
                print(f"  ... and {len(bodies) - 20} more")
                
        except Exception as e:
            print(f"Could not enumerate all bodies: {e}")
        
        # Restore original directory
        os.chdir(original_dir)
        return True
        
    except Exception as e:
        print(f"Error loading {name}: {e}")
        # Restore original directory even on error
        try:
            os.chdir(original_dir)
        except:
            pass
        return False

def main():
    print("Ephemeris Bodies Checker")
    print("Checking what celestial bodies are available in different ephemeris files")
    
    # Check different ephemeris files
    ephemeris_files = [
        ('de421.bsp', 'DE421 (1900-2050)'),
        ('de440.bsp', 'DE440 (1550-2650)'),
        ('de441.bsp', 'DE441 (-13200 to +17191)'),
        ('sb441-n16.bsp', 'SB441-N16 (Asteroid ephemeris)')
    ]
    
    results = {}
    for eph_file, name in ephemeris_files:
        results[name] = check_ephemeris(eph_file, name)
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for name, success in results.items():
        status = "✓ Loaded successfully" if success else "✗ Failed to load"
        print(f"{name}: {status}")

if __name__ == "__main__":
    main()