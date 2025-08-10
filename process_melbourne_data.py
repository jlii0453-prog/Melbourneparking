#!/usr/bin/env python3
"""
处理墨尔本SA2数据
将Shapefile转换为GeoJSON并过滤墨尔本地区
"""

import geopandas as gpd
import json
import requests

def load_sa2_data():
    """加载SA2 Shapefile数据"""
    print("正在加载SA2 Shapefile...")
    shapefile_path = r"D:\student\zfan_project\案例\resource\SA2_2021_AUST_SHP_GDA2020\SA2_2021_AUST_GDA2020.shp"
    
    # 读取Shapefile
    gdf = gpd.read_file(shapefile_path)
    
    print(f"总共加载了 {len(gdf)} 个SA2区域")
    print("数据列名:", list(gdf.columns))
    
    return gdf

def explore_data(gdf):
    """探索数据结构"""
    print("\n=== 数据探索 ===")
    print("前5行数据:")
    print(gdf.head())
    
    print("\n唯一的大首都城市区域:")
    if 'GCC_NAME21' in gdf.columns:
        gcc_names = gdf['GCC_NAME21'].unique()
        print(gcc_names)
    
    print("\n墨尔本相关区域数量:")
    melbourne_filter = gdf['GCC_NAME21'] == 'Greater Melbourne'
    melbourne_count = melbourne_filter.sum()
    print(f"大墨尔本地区有 {melbourne_count} 个SA2区域")
    
    return melbourne_filter

def filter_melbourne_data(gdf, melbourne_filter):
    """过滤墨尔本地区数据"""
    print("\n=== 过滤墨尔本数据 ===")
    
    # 过滤墨尔本地区
    melbourne_gdf = gdf[melbourne_filter].copy()
    
    # 转换坐标系到WGS84 (Google Maps使用的坐标系)
    melbourne_gdf = melbourne_gdf.to_crs('EPSG:4326')
    
    print(f"过滤后保留 {len(melbourne_gdf)} 个墨尔本SA2区域")
    
    # 显示一些SA2名称示例
    print("\n墨尔本SA2区域示例:")
    sa2_names = melbourne_gdf['SA2_NAME21'].head(10).tolist()
    for name in sa2_names:
        print(f"  - {name}")
    
    return melbourne_gdf

def create_geojson(melbourne_gdf):
    """创建GeoJSON文件"""
    print("\n=== 创建GeoJSON ===")
    
    # 转换为GeoJSON格式
    geojson = melbourne_gdf.to_json()
    
    # 保存GeoJSON文件
    with open('melbourne_sa2_boundaries.json', 'w', encoding='utf-8') as f:
        f.write(geojson)
    
    print("GeoJSON文件已保存为: melbourne_sa2_boundaries.json")
    
    return json.loads(geojson)

def create_bounds_info(melbourne_gdf):
    """创建边界信息文件（模拟zipcode_bound_info.json格式）"""
    print("\n=== 创建边界信息 ===")
    
    bounds_info = {"data": {}}
    
    for idx, row in melbourne_gdf.iterrows():
        sa2_name = row['SA2_NAME21']
        geometry = row['geometry']
        
        # 计算边界框
        bounds = geometry.bounds  # (minx, miny, maxx, maxy)
        
        # 计算中心点
        centroid = geometry.centroid
        
        # 格式: [min_lng, min_lat, max_lng, max_lat, center_lng, center_lat]
        bounds_info["data"][sa2_name] = [
            bounds[0],  # min_lng
            bounds[1],  # min_lat  
            bounds[2],  # max_lng
            bounds[3],  # max_lat
            centroid.x, # center_lng
            centroid.y  # center_lat
        ]
    
    # 保存边界信息文件
    with open('melbourne_sa2_bounds_info.json', 'w', encoding='utf-8') as f:
        json.dump(bounds_info, f, indent=2, ensure_ascii=False)
    
    print(f"边界信息文件已保存为: melbourne_sa2_bounds_info.json")
    print(f"包含 {len(bounds_info['data'])} 个SA2区域的边界信息")
    
    return bounds_info

def fetch_melbourne_population_data():
    """获取墨尔本人口数据"""
    print("\n=== 获取人口数据 ===")
    
    try:
        # 获取墨尔本全部数据
        url = 'https://vic-population-api.onrender.com/melbourne-city'
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("成功获取API数据")
            print(f"数据键值: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            # 保存原始API数据
            with open('melbourne_api_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return data
        else:
            print(f"API请求失败: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"获取API数据时出错: {e}")
        return None

def main():
    """主函数"""
    print("开始处理墨尔本SA2数据...")
    
    # 1. 加载Shapefile数据
    gdf = load_sa2_data()
    
    # 2. 探索数据
    melbourne_filter = explore_data(gdf)
    
    # 3. 过滤墨尔本数据
    melbourne_gdf = filter_melbourne_data(gdf, melbourne_filter)
    
    # 4. 创建GeoJSON
    geojson_data = create_geojson(melbourne_gdf)
    
    # 5. 创建边界信息
    bounds_info = create_bounds_info(melbourne_gdf)
    
    # 6. 获取人口数据
    api_data = fetch_melbourne_population_data()
    
    print("\n=== 处理完成 ===")
    print("生成的文件:")
    print("  - melbourne_sa2_boundaries.json (GeoJSON边界)")
    print("  - melbourne_sa2_bounds_info.json (边界信息)")
    print("  - melbourne_api_data.json (API人口数据)")
    
    print("\n下一步: 将这些文件集成到网站中")

if __name__ == "__main__":
    main()
