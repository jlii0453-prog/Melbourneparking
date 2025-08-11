#!/usr/bin/env python3
"""
计算墨尔本地图的最佳中心点和缩放级别
"""

import json
import math

def calculate_center_and_bounds():
    """计算墨尔本数据的地理中心和边界"""
    
    # 读取边界信息
    with open('zipcode_bound_info.json', 'r', encoding='utf-8') as f:
        bounds_data = json.load(f)
    
    regions = bounds_data['data']
    
    print(f"分析 {len(regions)} 个墨尔本SA2区域...")
    
    # 收集所有边界点
    all_lngs = []
    all_lats = []
    
    for region_name, bounds in regions.items():
        # bounds格式: [min_lng, min_lat, max_lng, max_lat, center_lng, center_lat]
        min_lng, min_lat, max_lng, max_lat, center_lng, center_lat = bounds
        
        all_lngs.extend([min_lng, max_lng])
        all_lats.extend([min_lat, max_lat])
    
    # 计算整体边界
    overall_min_lng = min(all_lngs)
    overall_max_lng = max(all_lngs)
    overall_min_lat = min(all_lats)
    overall_max_lat = max(all_lats)
    
    # 计算中心点
    center_lng = (overall_min_lng + overall_max_lng) / 2
    center_lat = (overall_min_lat + overall_max_lat) / 2
    
    # 计算跨度
    lng_span = overall_max_lng - overall_min_lng
    lat_span = overall_max_lat - overall_min_lat
    
    print("\n=== 地理边界分析 ===")
    print(f"经度范围: {overall_min_lng:.6f} 到 {overall_max_lng:.6f}")
    print(f"纬度范围: {overall_min_lat:.6f} 到 {overall_max_lat:.6f}")
    print(f"经度跨度: {lng_span:.6f}°")
    print(f"纬度跨度: {lat_span:.6f}°")
    print(f"建议中心点: ({center_lat:.6f}, {center_lng:.6f})")
    
    # 根据跨度估算合适的缩放级别
    # Google Maps缩放级别估算公式
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
    
    print(f"建议缩放级别: {zoom}")
    
    return center_lat, center_lng, zoom

def show_region_examples():
    """显示一些区域示例"""
    with open('zipcode_metadata.json', 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    print("\n=== 包含的墨尔本区域 ===")
    for region_name, population in metadata.items():
        print(f"  - {region_name}: {population:,} 人")

def main():
    """主函数"""
    print("计算墨尔本地图配置...")
    
    # 显示区域信息
    show_region_examples()
    
    # 计算中心点和缩放级别
    center_lat, center_lng, zoom = calculate_center_and_bounds()
    
    print(f"\n=== 推荐的地图配置 ===")
    print(f"中心点: {{lat: {center_lat:.6f}, lng: {center_lng:.6f}}}")
    print(f"缩放级别: {zoom}")
    
    print(f"\n=== 代码配置 ===")
    print(f"init_map_center: {{lat: {center_lat:.6f}, lng: {center_lng:.6f}}}")
    print(f"init_map_zoom: {zoom}")

if __name__ == "__main__":
    main()
