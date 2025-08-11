#!/usr/bin/env python3
"""
Process Melbourne SA2 data
Convert Shapefile to GeoJSON and filter the Melbourne area
"""

import geopandas as gpd
import json
import requests

def load_sa2_data():
    """Load SA2 Shapefile data"""
    print("Loading SA2 Shapefile...")
    shapefile_path = r"D:\student\zfan_project\案例\resource\SA2_2021_AUST_SHP_GDA2020\SA2_2021_AUST_GDA2020.shp"
    
    # Read Shapefile
    gdf = gpd.read_file(shapefile_path)
    
    print(f"Loaded a total of {len(gdf)} SA2 regions")
    print("Data column names:", list(gdf.columns))
    
    return gdf

def explore_data(gdf):
    """Explore data structure"""
    print("\n=== Data exploration ===")
    print("First 5 rows of data:")
    print(gdf.head())
    
    print("\nUnique Greater Capital City areas:")
    if 'GCC_NAME21' in gdf.columns:
        gcc_names = gdf['GCC_NAME21'].unique()
        print(gcc_names)
    
    print("\nNumber of Melbourne-related regions:")
    melbourne_filter = gdf['GCC_NAME21'] == 'Greater Melbourne'
    melbourne_count = melbourne_filter.sum()
    print(f"Greater Melbourne area has {melbourne_count} SA2 regions")
    
    return melbourne_filter

def filter_melbourne_data(gdf, melbourne_filter):
    """Filter Melbourne area data"""
    print("\n=== Filtering Melbourne data ===")
    
    # Filter Melbourne area
    melbourne_gdf = gdf[melbourne_filter].copy()
    
    # Convert coordinate system to WGS84 (coordinate system used by Google Maps)
    melbourne_gdf = melbourne_gdf.to_crs('EPSG:4326')
    
    print(f"After filtering, kept {len(melbourne_gdf)} Melbourne SA2 regions")
    
    # Show some SA2 name examples
    print("\nSample Melbourne SA2 regions:")
    sa2_names = melbourne_gdf['SA2_NAME21'].head(10).tolist()
    for name in sa2_names:
        print(f"  - {name}")
    
    return melbourne_gdf

def create_geojson(melbourne_gdf):
    """Create GeoJSON file"""
    print("\n=== Creating GeoJSON ===")
    
    # Convert to GeoJSON format
    geojson = melbourne_gdf.to_json()
    
    # Save GeoJSON file
    with open('melbourne_sa2_boundaries.json', 'w', encoding='utf-8') as f:
        f.write(geojson)
    
    print("GeoJSON file saved as: melbourne_sa2_boundaries.json")
    
    return json.loads(geojson)

def create_bounds_info(melbourne_gdf):
    """Create boundary info file (simulate zipcode_bound_info.json format)"""
    print("\n=== Creating boundary information ===")
    
    bounds_info = {"data": {}}
    
    for idx, row in melbourne_gdf.iterrows():
        sa2_name = row['SA2_NAME21']
        geometry = row['geometry']
        
        # Calculate bounding box
        bounds = geometry.bounds  # (minx, miny, maxx, maxy)
        
        # Calculate centroid
        centroid = geometry.centroid
        
        # Format: [min_lng, min_lat, max_lng, max_lat, center_lng, center_lat]
        bounds_info["data"][sa2_name] = [
            bounds[0],  # min_lng
            bounds[1],  # min_lat  
            bounds[2],  # max_lng
            bounds[3],  # max_lat
            centroid.x, # center_lng
            centroid.y  # center_lat
        ]
    
    # Save boundary info file
    with open('melbourne_sa2_bounds_info.json', 'w', encoding='utf-8') as f:
        json.dump(bounds_info, f, indent=2, ensure_ascii=False)
    
    print(f"Boundary information file saved as: melbourne_sa2_bounds_info.json")
    print(f"Contains boundary information for {len(bounds_info['data'])} SA2 regions")
    
    return bounds_info

def fetch_melbourne_population_data():
    """Fetch Melbourne population data"""
    print("\n=== Fetching population data ===")
    
    try:
        # Get all Melbourne data
        url = 'https://vic-population-api.onrender.com/melbourne-city'
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("Successfully fetched API data")
            print(f"Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            # Save raw API data
            with open('melbourne_api_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return data
        else:
            print(f"API request failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error fetching API data: {e}")
        return None

def main():
    """Main function"""
    print("Starting to process Melbourne SA2 data...")
    
    # 1. Load Shapefile data
    gdf = load_sa2_data()
    
    # 2. Explore data
    melbourne_filter = explore_data(gdf)
    
    # 3. Filter Melbourne data
    melbourne_gdf = filter_melbourne_data(gdf, melbourne_filter)
    
    # 4. Create GeoJSON
    geojson_data = create_geojson(melbourne_gdf)
    
    # 5. Create boundary information
    bounds_info = create_bounds_info(melbourne_gdf)
    
    # 6. Fetch population data
    api_data = fetch_melbourne_population_data()
    
    print("\n=== Processing completed ===")
    print("Generated files:")
    print("  - melbourne_sa2_boundaries.json (GeoJSON boundaries)")
    print("  - melbourne_sa2_bounds_info.json (boundary information)")
    print("  - melbourne_api_data.json (API population data)")
    
    print("\nNext step: Integrate these files into the website")

if __name__ == "__main__":
    main()
