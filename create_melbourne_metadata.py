#!/usr/bin/env python3
"""
创建墨尔本元数据文件
将API数据转换为zipcode_metadata.json的格式
"""

import json

def load_api_data():
    """加载API数据"""
    with open('melbourne_api_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def create_metadata_from_latest_year(api_data):
    """使用最新年份的人口数据创建元数据"""
    print("=== 创建人口元数据 ===")
    
    metadata = {}
    
    # 找到最新的年份列
    year_columns = [col for col in api_data[0].keys() if col.startswith('y')]
    latest_year = max(year_columns)
    
    print(f"使用 {latest_year} 年的人口数据")
    
    for region in api_data:
        sa2_name = region['sa2_name']
        population = region[latest_year]
        
        metadata[sa2_name] = population
    
    # 保存元数据文件
    with open('melbourne_population_metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"人口元数据已保存，包含 {len(metadata)} 个SA2区域")
    print(f"人口范围: {min(metadata.values())} - {max(metadata.values())} 人")
    
    return metadata

def create_density_metadata(api_data):
    """创建人口密度元数据"""
    print("\n=== 创建人口密度元数据 ===")
    
    metadata = {}
    
    # 找到最新的年份列
    year_columns = [col for col in api_data[0].keys() if col.startswith('y')]
    latest_year = max(year_columns)
    
    for region in api_data:
        sa2_name = region['sa2_name']
        population = region[latest_year]
        area_km2 = region['area_km2']
        
        # 计算人口密度 (人/平方公里)
        if area_km2 > 0:
            density = population / area_km2
        else:
            density = 0
        
        metadata[sa2_name] = round(density, 2)
    
    # 保存密度元数据文件
    with open('melbourne_density_metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"密度元数据已保存，包含 {len(metadata)} 个SA2区域")
    print(f"密度范围: {min(metadata.values())} - {max(metadata.values())} 人/km²")
    
    return metadata

def analyze_data_coverage(api_data, bounds_data):
    """分析数据覆盖情况"""
    print("\n=== 数据覆盖分析 ===")
    
    # API中的SA2名称
    api_sa2_names = set(region['sa2_name'] for region in api_data)
    
    # Shapefile中的SA2名称
    shapefile_sa2_names = set(bounds_data['data'].keys())
    
    # 交集
    common_names = api_sa2_names.intersection(shapefile_sa2_names)
    
    # 差集
    api_only = api_sa2_names - shapefile_sa2_names
    shapefile_only = shapefile_sa2_names - api_sa2_names
    
    print(f"API数据SA2数量: {len(api_sa2_names)}")
    print(f"Shapefile SA2数量: {len(shapefile_sa2_names)}")
    print(f"匹配的SA2数量: {len(common_names)}")
    print(f"只在API中的SA2: {len(api_only)}")
    print(f"只在Shapefile中的SA2: {len(shapefile_only)}")
    
    if api_only:
        print("\n只在API中的SA2示例:")
        for name in list(api_only)[:5]:
            print(f"  - {name}")
    
    if shapefile_only:
        print("\n只在Shapefile中的SA2示例:")
        for name in list(shapefile_only)[:5]:
            print(f"  - {name}")
    
    # 创建只包含匹配区域的元数据
    return common_names

def create_matched_metadata(api_data, common_names):
    """创建只包含匹配区域的元数据"""
    print("\n=== 创建匹配的元数据 ===")
    
    # 人口数据
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
    
    # 保存匹配的元数据文件
    with open('zipcode_metadata.json', 'w', encoding='utf-8') as f:
        json.dump(population_metadata, f, indent=2, ensure_ascii=False)
    
    with open('melbourne_density_matched.json', 'w', encoding='utf-8') as f:
        json.dump(density_metadata, f, indent=2, ensure_ascii=False)
    
    print(f"匹配的人口元数据已保存到 zipcode_metadata.json: {len(population_metadata)} 个区域")
    print(f"匹配的密度元数据已保存到 melbourne_density_matched.json: {len(density_metadata)} 个区域")
    
    return population_metadata, density_metadata

def main():
    """主函数"""
    print("开始处理墨尔本API数据...")
    
    # 1. 加载API数据
    api_data = load_api_data()
    print(f"加载了 {len(api_data)} 个SA2区域的API数据")
    
    # 2. 加载边界数据
    with open('melbourne_sa2_bounds_info.json', 'r', encoding='utf-8') as f:
        bounds_data = json.load(f)
    
    # 3. 分析数据覆盖
    common_names = analyze_data_coverage(api_data, bounds_data)
    
    # 4. 创建匹配的元数据
    population_metadata, density_metadata = create_matched_metadata(api_data, common_names)
    
    # 5. 也创建完整的元数据供参考
    create_metadata_from_latest_year(api_data)
    create_density_metadata(api_data)
    
    print("\n=== 处理完成 ===")
    print("生成的文件:")
    print("  - zipcode_metadata.json (匹配的人口数据)")
    print("  - melbourne_density_matched.json (匹配的密度数据)")
    print("  - melbourne_population_metadata.json (完整人口数据)")
    print("  - melbourne_density_metadata.json (完整密度数据)")

if __name__ == "__main__":
    main()
