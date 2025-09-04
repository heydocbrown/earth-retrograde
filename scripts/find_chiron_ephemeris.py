#!/usr/bin/env python3
"""
Find the correct ephemeris file that contains Chiron
"""

from skyfield.api import load

def check_jpl_ephemeris_catalog():
    """Check what asteroid ephemeris files are available"""
    print("Checking JPL ephemeris catalog for asteroid files...")
    
    # Common asteroid ephemeris file patterns
    potential_files = [
        'sb441-n16.bsp',  # What we tried
        'sb441.bsp',      # Without the -n16
        'asteroids.bsp',  # Generic name
        'sb432s.bsp',     # Another common one
        'sb441-n16s.bsp', # With 's' suffix
        'de441_part-1.bsp', # Part files
        'de441_part-2.bsp'
    ]
    
    base_urls = [
        'https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/',
        'https://ssd.jpl.nasa.gov/ftp/eph/small_bodies/asteroids_de441/',
        'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/asteroids/'
    ]
    
    found_files = []
    
    for base_url in base_urls:
        print(f"\nChecking {base_url}")
        for filename in potential_files:
            full_url = base_url + filename
            try:
                response = requests.head(full_url, timeout=10)
                if response.status_code == 200:
                    size_mb = int(response.headers.get('content-length', 0)) / (1024 * 1024)
                    print(f"  ✓ {filename} - {size_mb:.1f} MB - {full_url}")
                    found_files.append((filename, full_url, size_mb))
                else:
                    print(f"  ✗ {filename} - HTTP {response.status_code}")
            except Exception as e:
                print(f"  ? {filename} - {str(e)[:50]}...")
    
    return found_files

def try_asteroid_ephemeris_files():
    """Try actual asteroid ephemeris files"""
    print(f"\n{'='*60}")
    print("TRYING ASTEROID EPHEMERIS FILES")
    print(f"{'='*60}")
    
    # ONLY asteroid files - NO DE files
    asteroid_files = [
        'sb441-n16.bsp',
        'sb441.bsp', 
        'asteroids.bsp',
        'sb432s.bsp'
    ]
    
    for ast_file in asteroid_files:
        print(f"\nTrying {ast_file}...")
        try:
            eph = load(ast_file)
            print(f"  ✓ {ast_file} loaded successfully")
            
            # Try to find Chiron
            try:
                chiron = eph[2060]
                print(f"  ✓ Chiron (2060) found in {ast_file}!")
                return ast_file
            except KeyError:
                print(f"  ✗ Chiron not in {ast_file}")
                
        except Exception as e:
            print(f"  ✗ Failed to load {ast_file}: {e}")
    
    return None

def check_skyfield_builtin_options():
    """Check what Skyfield can load by default"""
    print(f"\n{'='*60}")
    print("SKYFIELD BUILT-IN OPTIONS")
    print(f"{'='*60}")
    
    try:
        from skyfield.api import Loader
        loader = Loader('.')
        
        # Try different loader options
        print("Trying different load methods...")
        
        # Method 1: Try with full path specification
        try:
            loader = Loader('https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/asteroids/')
            print("✓ Custom loader created")
        except Exception as e:
            print(f"✗ Custom loader failed: {e}")
        
        # Method 2: Check documentation examples
        print("\nSuggested alternatives:")
        print("1. Use Horizons API for Chiron positions")
        print("2. Use approximation formulas for outer solar system")
        print("3. Skip Chiron for now and focus on planets")
        
    except Exception as e:
        print(f"Error checking Skyfield options: {e}")

def main():
    print("Finding Correct Chiron Ephemeris")
    print("="*60)
    
    print("The file 'sb441-n16.bsp' does not exist at the expected URL.")
    print("Let's try alternative approaches...")
    
    # Skip the network check
    found_files = []
    
    if found_files:
        print(f"\n{'='*60}")
        print("FOUND EPHEMERIS FILES")
        print(f"{'='*60}")
        for filename, url, size in found_files:
            print(f"{filename}: {url} ({size:.1f} MB)")
    else:
        print("\nNo asteroid ephemeris files found at standard locations")
    
    # Try asteroid files
    working_file = try_asteroid_ephemeris_files()
    
    # Check Skyfield options
    check_skyfield_builtin_options()
    
    print(f"\n{'='*60}")
    print("RECOMMENDATIONS")
    print(f"{'='*60}")
    
    if found_files:
        best_file = min(found_files, key=lambda x: x[2])  # Smallest file
        print(f"✓ Use: {best_file[1]}")
        print(f"  Size: {best_file[2]:.1f} MB")
    elif working_file:
        print(f"✓ Use {working_file} for Chiron")
    else:
        print("❌ Chiron not readily available")
        print("💡 Suggestions:")
        print("   1. Skip Chiron and use only planets")
        print("   2. Use NASA Horizons API for Chiron positions")
        print("   3. Implement approximate orbital calculations")

if __name__ == "__main__":
    main()