#!/usr/bin/env python3
"""
Calculate the optimal center point and zoom level for the Melbourne map
"""

import json
import math

def calculate_center_and_bounds():
    """Calculate the geographic center and boundaries of Melbourne data"""
    
    # Read boundary information
    with open('zipcode_bound_info.json', 'r', encoding='utf-8') as f:
        bounds_data = json.load(f)
    
    regions = bounds_data['data']
    
    print(f"Analyzing {len(regions)} Melbourne SA2 regions...")
    
    # Collect all boundary points
    all_lngs = []
    all_lats = []
    
    for region_name, bounds in regions.items():
        # bounds format: [min_lng, min_lat, max_lng, max_lat, center_lng, center_lat]
        min_lng, min_lat, max_lng, max_lat, center_lng, center_lat = bounds
        
        all_lngs.extend([min_lng, max_lng])
        all_lats.extend([min_lat, max_lat])
    
    # Calculate overall boundary
    overall_min_lng = min(all_lngs)
    overall_max_lng = max(all_lngs)
    overall_min_lat = min(all_lats)
    overall_max_lat = max(all_lats)
    
    # Calculate center point
    center_lng = (overall_min_lng + overall_max_lng) / 2
    center_lat = (overall_min_lat + overall_max_lat) / 2
    
    # Calculate span
    lng_span = overall_max_lng - overall_min_lng
    lat_span = overall_max_lat - overall_min_lat
    
    print("\n=== Geographic Boundary Analysis ===")
    print(f"Longitude range: {overall_min_lng:.6f} to {overall_max_lng:.6f}")
    print(f"Latitude range: {overall_min_lat:.6f} to {overall_max_lat:.6f}")
    print(f"Longitude span: {lng_span:.6f}°")
    print(f"Latitude span: {lat_span:.6f}°")
    print(f"Suggested center point: ({center_lat:.6f}, {center_lng:.6f})")
    
    # Estimate appropriate zoom level based on span
    # Google Maps zoom level estimation formula
    max_span = max(lng_span, lat_span)
    
    if max_span > 10:
        zoom = 8
    elif max_span > 5:
        zoom = 9
    elif max_span > 2:
        zoom = 10
    elif max_span > 1:
        zoom = 11
    elif max_span > 0.5:
        zoom = 12
    elif max_span > 0.2:
        zoom = 13
    elif max_span > 0.1:
        zoom = 14
    else:
        zoom = 15
    
    print(f"Suggested zoom level: {zoom}")
    
    return center_lat, center_lng, zoom

def show_region_examples():
    """Show some region examples"""
    with open('zipcode_metadata.json', 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    print("\n=== Included Melbourne Regions ===")
    for region_name, population in metadata.items():
        print(f"  - {region_name}: {population:,} people")

def main():
    """Main function"""
    print("Calculating Melbourne map configuration...")
    
    # Show region information
    show_region_examples()
    
    # Calculate center point and zoom level
    center_lat, center_lng, zoom = calculate_center_and_bounds()
    
    print(f"\n=== Recommended Map Configuration ===")
    print(f"Center point: {{lat: {center_lat:.6f}, lng: {center_lng:.6f}}}")
    print(f"Zoom level: {zoom}")
    
    print(f"\n=== Code Configuration ===")
    print(f"init_map_center: {{lat: {center_lat:.6f}, lng: {center_lng:.6f}}}")
    print(f"init_map_zoom: {zoom}")

if __name__ == "__main__":
    main()
