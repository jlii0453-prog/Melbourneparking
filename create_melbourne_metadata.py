#!/usr/bin/env python3
"""
Create Melbourne metadata files
Convert API data into the format of zipcode_metadata.json
"""

import json
import requests
import os

API_URL = os.getenv("POP_API_URL", "https://vic-population-api.onrender.com/melbourne-city")
LOCAL_JSON = "melbourne_api_data.json"

def load_api_data():
    """
    Prefer to fetch data from the online API; fallback to local melbourne_api_data.json if failed
    Expected API returns each record containing fields:
    sa2_name, area_km2, y2001...y2021
    """
    print(f"[INFO] Fetching API: {API_URL}")
    r = requests.get(API_URL, timeout=20)
    r.raise_for_status()
    data = r.json()

    if not data or "sa2_name" not in data[0]:
        raise ValueError("API response structure does not contain 'sa2_name'")

    with open(LOCAL_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[INFO] Written to {LOCAL_JSON}, records: {len(data)}")

    return data
    
def create_metadata_from_latest_year(api_data):
    """Create metadata using the latest year's population data"""
    print("=== Creating population metadata ===")
    
    metadata = {}
    
    # Find the latest year column
    year_columns = [col for col in api_data[0].keys() if col.startswith('y')]
    latest_year = max(year_columns)
    
    print(f"Using population data from year {latest_year}")
    
    for region in api_data:
        sa2_name = region['sa2_name']
        population = region[latest_year]
        
        metadata[sa2_name] = population
    
    # Save metadata file
    with open('melbourne_population_metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"Population metadata saved, contains {len(metadata)} SA2 regions")
    print(f"Population range: {min(metadata.values())} - {max(metadata.values())} people")
    
    return metadata

def create_density_metadata(api_data):
    """Create population density metadata"""
    print("\n=== Creating population density metadata ===")
    
    metadata = {}
    
    # Find the latest year column
    year_columns = [col for col in api_data[0].keys() if col.startswith('y')]
    latest_year = max(year_columns)
    
    for region in api_data:
        sa2_name = region['sa2_name']
        population = region[latest_year]
        area_km2 = region['area_km2']
        
        # Calculate population density (people/km²)
        if area_km2 > 0:
            density = population / area_km2
        else:
            density = 0
        
        metadata[sa2_name] = round(density, 2)
    
    # Save density metadata file
    with open('melbourne_density_metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"Density metadata saved, contains {len(metadata)} SA2 regions")
    print(f"Density range: {min(metadata.values())} - {max(metadata.values())} people/km²")
    
    return metadata

def analyze_data_coverage(api_data, bounds_data):
    """Analyze data coverage"""
    print("\n=== Data coverage analysis ===")
    
    # SA2 names in API
    api_sa2_names = set(region['sa2_name'] for region in api_data)
    
    # SA2 names in Shapefile
    shapefile_sa2_names = set(bounds_data['data'].keys())
    
    # Intersection
    common_names = api_sa2_names.intersection(shapefile_sa2_names)
    
    # Differences
    api_only = api_sa2_names - shapefile_sa2_names
    shapefile_only = shapefile_sa2_names - api_sa2_names
    
    print(f"SA2 count in API data: {len(api_sa2_names)}")
    print(f"SA2 count in Shapefile: {len(shapefile_sa2_names)}")
    print(f"Matched SA2 count: {len(common_names)}")
    print(f"SA2 only in API: {len(api_only)}")
    print(f"SA2 only in Shapefile: {len(shapefile_only)}")
    
    if api_only:
        print("\nExamples of SA2 only in API:")
        for name in list(api_only)[:5]:
            print(f"  - {name}")
    
    if shapefile_only:
        print("\nExamples of SA2 only in Shapefile:")
        for name in list(shapefile_only)[:5]:
            print(f"  - {name}")
    
    # Create metadata containing only matched regions
    return common_names

def create_matched_metadata(api_data, common_names):
    """Create metadata containing only matched regions"""
    print("\n=== Creating matched metadata ===")
    
    # Population data
    population_metadata = {}
    density_metadata = {}
    
    year_columns = [col for col in api_data[0].keys() if col.startswith('y')]
    latest_year = max(year_columns)
    
    for region in api_data:
        sa2_name = region['sa2_name']
        
        if sa2_name in common_names:
            population = region[latest_year]
            area_km2 = region['area_km2']
            
            population_metadata[sa2_name] = population
            
            if area_km2 > 0:
                density = population / area_km2
            else:
                density = 0
            
            density_metadata[sa2_name] = round(density, 2)
    
    # Save matched metadata files
    with open('zipcode_metadata.json', 'w', encoding='utf-8') as f:
        json.dump(population_metadata, f, indent=2, ensure_ascii=False)
    
    with open('melbourne_density_matched.json', 'w', encoding='utf-8') as f:
        json.dump(density_metadata, f, indent=2, ensure_ascii=False)
    
    print(f"Matched population metadata saved to zipcode_metadata.json: {len(population_metadata)} regions")
    print(f"Matched density metadata saved to melbourne_density_matched.json: {len(density_metadata)} regions")
    
    return population_metadata, density_metadata

def main():
    """Main function"""
    print("Starting to process Melbourne API data...")
    
    # 1. Load API data
    try:
        api_data = load_api_data()  # Will fetch API and update melbourne_api_data.json
    except Exception as e:
        print(f"[WARN] API fetch failed, falling back to local file. Reason: {e}")
        with open(LOCAL_JSON, 'r', encoding='utf-8') as f:
            api_data = json.load(f)
    print(f"Loaded {len(api_data)} SA2 regions from API data")
    
    # 2. Load boundary data
    with open('melbourne_sa2_bounds_info.json', 'r', encoding='utf-8') as f:
        bounds_data = json.load(f)
    
    # 3. Analyze data coverage
    common_names = analyze_data_coverage(api_data, bounds_data)
    
    # 4. Create matched metadata
    population_metadata, density_metadata = create_matched_metadata(api_data, common_names)
    
    # 5. Also create complete metadata for reference
    create_metadata_from_latest_year(api_data)
    create_density_metadata(api_data)
    
    print("\n=== Processing completed ===")
    print("Generated files:")
    print("  - zipcode_metadata.json (matched population data)")
    print("  - melbourne_density_matched.json (matched density data)")
    print("  - melbourne_population_metadata.json (full population data)")
    print("  - melbourne_density_metadata.json (full density data)")

if __name__ == "__main__":
    main()
