import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import random

class SalesDataProcessor:
    """销售数据处理器，用于分析现有数据并生成测试数据"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.required_columns = ['Order_ID', 'Product', 'Quantity', 'Price', 'Order_Date', 'Region']
        
    def analyze_existing_data(self):
        """分析现有数据文件，检查是否符合要求"""
        print("=== 分析现有数据文件 ===")
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.csv'):
                filepath = os.path.join(self.data_dir, filename)
                print(f"\n分析文件: {filename}")
                
                try:
                    # 读取文件前几行来检查结构
                    df = pd.read_csv(filepath, nrows=5)
                    print(f"文件列: {list(df.columns)}")
                    print(f"文件形状: {df.shape}")
                    
                    # 检查是否包含所有必需列
                    missing_cols = [col for col in self.required_columns if col not in df.columns]
                    if missing_cols:
                        print(f"❌ 缺少必需列: {missing_cols}")
                        return False
                    else:
                        print("✅ 包含所有必需列")
                        
                    # 检查完整文件
                    df_full = pd.read_csv(filepath)
                    print(f"完整文件形状: {df_full.shape}")
                    print(f"缺失值统计:")
                    for col in self.required_columns:
                        missing_count = df_full[col].isnull().sum()
                        missing_percent = (missing_count / len(df_full)) * 100
                        print(f"  {col}: {missing_count} ({missing_percent:.1f}%)")
                        
                except Exception as e:
                    print(f"❌ 读取文件失败: {e}")
                    
        return True
    
    def generate_test_data(self):
        """生成多种不同方向的测试数据文件"""
        print("\n=== 生成测试数据文件 ===")
        
        # 产品列表
        products = [
            # 电子产品
            'Laptop', 'Desktop', 'Tablet', 'Smartphone', 'Monitor', 'Keyboard', 'Mouse',
            'Headphones', 'Speaker', 'Webcam', 'Microphone', 'Printer', 'Scanner',
            # 硬件组件
            'Motherboard', 'CPU', 'GPU', 'Graphics Card', 'RAM', 'SSD', 'HDD', 'External HDD',
            'Power Supply', 'Cooling Fan', 'USB Drive', 'Network Card',
            # 办公用品
            'Office Chair', 'Desk', 'Notebook', 'Pen', 'Paper', 'Folder', 'Calculator',
            # 家电
            'Air Conditioner', 'Refrigerator', 'Washing Machine', 'Microwave', 'TV',
            # 服装
            'T-Shirt', 'Jeans', 'Jacket', 'Shoes', 'Hat', 'Bag', 'Watch',
            # 书籍
            'Programming Book', 'Novel', 'Textbook', 'Magazine', 'Dictionary'
        ]
        
        # 地区列表
        regions = ['North', 'South', 'East', 'West', 'Central', 'Northeast', 'Northwest', 'Southeast', 'Southwest']
        
        # 生成不同类型的测试数据
        test_datasets = {
            'small_dataset': 500,      # 小数据集
            'medium_dataset': 2000,    # 中等数据集
            'large_dataset': 10000,    # 大数据集
            'high_missing_dataset': 1000,  # 高缺失值数据集
            'seasonal_dataset': 3000,   # 季节性数据集
            'regional_focus_dataset': 1500,  # 地区重点数据集
            'product_category_dataset': 2500,  # 产品类别数据集
        }
        
        for dataset_name, size in test_datasets.items():
            print(f"生成 {dataset_name} ({size} 条记录)...")
            df = self._generate_dataset(dataset_name, size, products, regions)
            filename = f"{dataset_name}.csv"
            filepath = os.path.join(self.data_dir, filename)
            df.to_csv(filepath, index=False)
            print(f"  保存到: {filename}")
            
    def _generate_dataset(self, dataset_type, size, products, regions):
        """生成特定类型的数据集"""
        
        # 基础数据框架
        data = {
            'Order_ID': range(1, size + 1),
            'Product': [random.choice(products) for _ in range(size)],
            'Quantity': [random.randint(1, 50) for _ in range(size)],
            'Price': [round(random.uniform(10, 1000), 2) for _ in range(size)],
            'Order_Date': [],
            'Region': [random.choice(regions) for _ in range(size)]
        }
        
        # 生成日期
        if dataset_type == 'seasonal_dataset':
            # 季节性数据 - 主要集中在特定月份
            seasonal_months = [11, 12, 1, 2]  # 主要在年末年初
            for _ in range(size):
                if random.random() < 0.7:  # 70%的数据在季节性月份
                    month = random.choice(seasonal_months)
                    year = random.choice([2022, 2023, 2024])
                    day = random.randint(1, 28)
                else:
                    month = random.randint(1, 12)
                    year = random.choice([2022, 2023, 2024])
                    day = random.randint(1, 28)
                
                date = datetime(year, month, day)
                data['Order_Date'].append(date.strftime('%Y-%m-%d'))
        else:
            # 常规日期分布
            start_date = datetime(2022, 1, 1)
            end_date = datetime(2024, 12, 31)
            for _ in range(size):
                random_date = start_date + timedelta(
                    days=random.randint(0, (end_date - start_date).days)
                )
                data['Order_Date'].append(random_date.strftime('%Y-%m-%d'))
        
        df = pd.DataFrame(data)
        
        # 根据数据集类型调整特征
        if dataset_type == 'high_missing_dataset':
            # 高缺失值数据集
            # Price列30%缺失
            missing_price_indices = random.sample(range(size), int(size * 0.3))
            df.loc[missing_price_indices, 'Price'] = np.nan
            
            # Region列20%缺失
            missing_region_indices = random.sample(range(size), int(size * 0.2))
            df.loc[missing_region_indices, 'Region'] = np.nan
            
        elif dataset_type == 'regional_focus_dataset':
            # 地区重点数据集 - 主要集中在某些地区
            focus_regions = ['North', 'South']
            for i in range(size):
                if random.random() < 0.8:  # 80%的数据集中在重点地区
                    df.loc[i, 'Region'] = random.choice(focus_regions)
                    
        elif dataset_type == 'product_category_dataset':
            # 产品类别数据集 - 主要是电子产品
            electronics = ['Laptop', 'Desktop', 'Tablet', 'Smartphone', 'Monitor', 'Keyboard', 'Mouse']
            for i in range(size):
                if random.random() < 0.7:  # 70%是电子产品
                    df.loc[i, 'Product'] = random.choice(electronics)
                    
        # 添加一些随机缺失值（除了high_missing_dataset）
        if dataset_type != 'high_missing_dataset':
            # Price列10%缺失
            missing_price_indices = random.sample(range(size), int(size * 0.1))
            df.loc[missing_price_indices, 'Price'] = np.nan
            
            # Region列5%缺失
            missing_region_indices = random.sample(range(size), int(size * 0.05))
            df.loc[missing_region_indices, 'Region'] = np.nan
        
        return df
    
    def clean_data_directory(self):
        """清理数据目录，移除不符合要求的文件"""
        print("\n=== 清理数据目录 ===")
        
        valid_files = []
        invalid_files = []
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.csv'):
                filepath = os.path.join(self.data_dir, filename)
                
                try:
                    df = pd.read_csv(filepath, nrows=5)
                    missing_cols = [col for col in self.required_columns if col not in df.columns]
                    
                    if missing_cols:
                        invalid_files.append(filename)
                        print(f"❌ 将删除: {filename} (缺少列: {missing_cols})")
                    else:
                        valid_files.append(filename)
                        print(f"✅ 保留: {filename}")
                        
                except Exception as e:
                    invalid_files.append(filename)
                    print(f"❌ 将删除: {filename} (读取错误: {e})")
        
        # 删除无效文件
        for filename in invalid_files:
            filepath = os.path.join(self.data_dir, filename)
            try:
                os.remove(filepath)
                print(f"已删除: {filename}")
            except Exception as e:
                print(f"删除失败 {filename}: {e}")
        
        print(f"\n清理完成! 保留 {len(valid_files)} 个文件，删除 {len(invalid_files)} 个文件")
        
    def generate_summary_report(self):
        """生成数据概况报告"""
        print("\n=== 生成数据概况报告 ===")
        
        report = []
        report.append("# 销售数据集概况报告")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        total_records = 0
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.csv'):
                filepath = os.path.join(self.data_dir, filename)
                try:
                    df = pd.read_csv(filepath)
                    total_records += len(df)
                    
                    report.append(f"## {filename}")
                    report.append(f"- 记录数: {len(df):,}")
                    report.append(f"- 列数: {len(df.columns)}")
                    report.append(f"- 日期范围: {df['Order_Date'].min()} 到 {df['Order_Date'].max()}")
                    report.append(f"- 产品种类: {df['Product'].nunique()}")
                    report.append(f"- 地区数量: {df['Region'].nunique()}")
                    report.append(f"- Price缺失率: {(df['Price'].isnull().sum() / len(df) * 100):.1f}%")
                    report.append(f"- Region缺失率: {(df['Region'].isnull().sum() / len(df) * 100):.1f}%")
                    report.append("")
                    
                except Exception as e:
                    report.append(f"## {filename}")
                    report.append(f"- 错误: {e}")
                    report.append("")
        
        report.append(f"## 总计")
        report.append(f"- 总记录数: {total_records:,}")
        report.append(f"- 数据文件数: {len([f for f in os.listdir(self.data_dir) if f.endswith('.csv')])}")
        
        # 保存报告
        report_path = os.path.join(self.data_dir, "data_summary_report.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        print(f"报告已保存到: {report_path}")
        
        # 同时打印到控制台
        print("\n" + '\n'.join(report))

def main():
    """主函数"""
    processor = SalesDataProcessor()
    
    print("销售数据处理工具")
    print("=" * 50)
    
    # 1. 分析现有数据
    processor.analyze_existing_data()
    
    # 2. 生成测试数据
    processor.generate_test_data()
    
    # 3. 生成概况报告
    processor.generate_summary_report()
    
    print("\n处理完成!")
    print("现在您可以使用这些数据文件进行销售数据分析项目。")

if __name__ == "__main__":
    main() 