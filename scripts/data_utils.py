import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def create_sample_sales_data(n_records=1000):
    """
    创建符合项目要求的销售数据样本
    """
    # 设置随机种子以确保结果可重现
    np.random.seed(42)
    random.seed(42)
    
    # 产品列表
    products = [
        "Laptop", "Smartphone", "Tablet", "Headphones", "Mouse", "Keyboard", 
        "Monitor", "Printer", "Camera", "Speaker", "Microphone", "Webcam",
        "USB Drive", "External HDD", "RAM", "SSD", "Graphics Card", "Motherboard",
        "Power Supply", "Cooling Fan"
    ]
    
    # 地区列表
    regions = ["North", "South", "East", "West", "Central"]
    
    # 生成数据
    data = []
    start_date = datetime(2023, 1, 1)
    
    for i in range(n_records):
        # 订单ID
        order_id = i + 1
        
        # 产品名称
        product = random.choice(products)
        
        # 购买数量 (1-50)
        quantity = random.randint(1, 50)
        
        # 产品单价 (10-1000)
        price = round(random.uniform(10, 1000), 2)
        
        # 订单日期
        days_offset = random.randint(0, 365)
        order_date = start_date + timedelta(days=days_offset)
        
        # 销售地区
        region = random.choice(regions)
        
        data.append({
            'Order_ID': order_id,
            'Product': product,
            'Quantity': quantity,
            'Price': price,
            'Order_Date': order_date.strftime('%Y-%m-%d'),
            'Region': region
        })
    
    df = pd.DataFrame(data)
    
    # 添加一些缺失值
    # Price缺失值
    price_missing_indices = random.sample(range(len(df)), int(len(df) * 0.1))
    df.loc[price_missing_indices, 'Price'] = np.nan
    
    # Region缺失值
    region_missing_indices = random.sample(range(len(df)), int(len(df) * 0.05))
    df.loc[region_missing_indices, 'Region'] = np.nan
    
    return df

def load_and_check_data(file_path):
    """
    加载数据并进行基本检查
    """
    print("=== 数据加载与检查 ===")
    
    # 读取数据
    df = pd.read_csv(file_path)
    
    # 显示前3行
    print("\n1. 数据前3行:")
    print(df.head(3))
    
    # 数据维度
    print(f"\n2. 数据维度: {df.shape[0]} 行 × {df.shape[1]} 列")
    
    # 数据类型
    print("\n3. 数据类型:")
    print(df.dtypes)
    
    # 检查Quantity列缺失值
    quantity_missing = df['Quantity'].isnull().sum()
    print(f"\n4. Quantity列缺失值数量: {quantity_missing}")
    
    return df

def clean_data(df):
    """
    数据清洗
    """
    print("\n=== 数据清洗 ===")
    
    # 记录清洗前的行数
    initial_rows = len(df)
    print(f"清洗前行数: {initial_rows}")
    
    # 1. 处理Price缺失值 - 用中位数填充
    price_median = df['Price'].median()
    df['Price'].fillna(price_median, inplace=True)
    print(f"Price列缺失值已用中位数 {price_median:.2f} 填充")
    
    # 2. 处理Region缺失值 - 用"Unknown"填充
    df['Region'].fillna('Unknown', inplace=True)
    print("Region列缺失值已用'Unknown'填充")
    
    # 3. 删除完全重复的行
    df.drop_duplicates(inplace=True)
    print(f"删除重复行后行数: {len(df)}")
    
    # 4. 将Order_Date列转换为日期格式
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])
    print("Order_Date列已转换为日期格式")
    
    return df

def handle_outliers(df):
    """
    异常值处理
    """
    print("\n=== 异常值处理 ===")
    
    # 计算Quantity列的IQR
    Q1 = df['Quantity'].quantile(0.25)
    Q3 = df['Quantity'].quantile(0.75)
    IQR = Q3 - Q1
    upper_bound = Q3 + 1.5 * IQR
    
    print(f"Quantity列统计:")
    print(f"Q1: {Q1}")
    print(f"Q3: {Q3}")
    print(f"IQR: {IQR}")
    print(f"上界: {upper_bound}")
    
    # 统计异常值数量
    outliers_before = len(df[df['Quantity'] > upper_bound])
    print(f"处理前异常值数量: {outliers_before}")
    
    # 替换异常值
    df.loc[df['Quantity'] > upper_bound, 'Quantity'] = upper_bound
    
    outliers_after = len(df[df['Quantity'] > upper_bound])
    print(f"处理后异常值数量: {outliers_after}")
    
    return df

def exploratory_analysis(df):
    """
    探索性分析
    """
    print("\n=== 探索性分析 ===")
    
    # 1. 描述统计
    print("1. 数值列描述统计:")
    numeric_cols = ['Quantity', 'Price']
    print(df[numeric_cols].describe())
    
    # 2. 新增Sales列
    df['Sales'] = df['Quantity'] * df['Price']
    print("\n2. 已新增Sales列 (Quantity × Price)")
    
    # 3. 按Region分组计算
    print("\n3. 按Region分组统计:")
    grouped = df.groupby('Region').agg({
        'Sales': ['sum', 'mean']
    }).round(2)
    
    # 重命名列为中英文对照
    grouped.columns = ['总销售额 (Total Sales)', '平均订单金额 (Avg Order Value)']
    print(grouped)
    
    return df, grouped

def save_results(df, grouped, output_dir):
    """
    保存结果
    """
    # 保存清洗后的数据
    cleaned_file = f"{output_dir}/cleaned_data.csv"
    df.to_csv(cleaned_file, index=False, encoding='utf-8-sig')
    print(f"\n清洗后的数据已保存到: {cleaned_file}")
    
    # 保存分组统计
    summary_file = f"{output_dir}/summary_stats.csv"
    grouped.to_csv(summary_file, encoding='utf-8-sig')
    print(f"分组统计已保存到: {summary_file}")
    
    return cleaned_file, summary_file 