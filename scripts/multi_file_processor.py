#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多文件销售数据处理器

支持批量处理多个CSV/XLSX文件的销售数据分析
"""

import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class MultiFileProcessor:
    """多文件处理器类"""
    
    def __init__(self):
        self.processed_files = {}
        self.combined_data = None
        self.file_summaries = {}
        
    def scan_directory(self, directory_path="data"):
        """扫描目录中的所有CSV和XLSX文件（包括子文件夹）"""
        files = []
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"目录不存在: {directory_path}")
        
        print(f"🔍 开始递归扫描目录: {directory_path}")
        
        # 递归扫描CSV文件
        csv_files = list(directory.rglob("*.csv"))
        xlsx_files = list(directory.rglob("*.xlsx"))
        
        print(f"📁 发现 CSV 文件: {len(csv_files)} 个")
        print(f"📁 发现 XLSX 文件: {len(xlsx_files)} 个")
        
        # 合并所有文件
        all_files = csv_files + xlsx_files
        
        # 打印文件路径信息
        for file_path in sorted(all_files):
            relative_path = file_path.relative_to(directory)
            file_size = file_path.stat().st_size / (1024 * 1024)  # MB
            print(f"  📄 {relative_path} ({file_size:.2f} MB)")
        
        return sorted([str(f) for f in all_files])
    
    def load_file(self, file_path):
        """加载单个文件，自动检测文件类型"""
        try:
            file_path = Path(file_path)
            print(f"      ┌─ 开始加载文件: {file_path.name}")
            print(f"      ├─ 文件大小: {file_path.stat().st_size / (1024 * 1024):.2f} MB")
            
            if file_path.suffix.lower() == '.csv':
                print(f"      ├─ 文件类型: CSV")
                # 尝试不同的编码
                for encoding in ['utf-8', 'gbk', 'latin-1']:
                    try:
                        print(f"      ├─ 尝试编码: {encoding}")
                        df = pd.read_csv(file_path, encoding=encoding)
                        print(f"      ├─ 编码成功: {encoding}")
                        break
                    except UnicodeDecodeError as e:
                        print(f"      ├─ 编码失败: {encoding} - {str(e)}")
                        continue
                else:
                    raise Exception("无法读取CSV文件，编码问题")
                    
            elif file_path.suffix.lower() == '.xlsx':
                print(f"      ├─ 文件类型: XLSX")
                df = pd.read_excel(file_path)
            else:
                raise Exception(f"不支持的文件格式: {file_path.suffix}")
            
            print(f"      ├─ 文件加载成功")
            print(f"      ├─ 数据维度: {df.shape[0]} 行 x {df.shape[1]} 列")
            print(f"      └─ 列名: {list(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
            
            return df
            
        except Exception as e:
            print(f"      └─ 文件加载失败: {str(e)}")
            raise Exception(f"加载文件失败 {file_path}: {str(e)}")
    
    def standardize_columns(self, df, file_name):
        """标准化列名，尝试识别销售数据的关键列"""
        
        # 常见的列名映射
        column_mapping = {
            # 订单ID相关
            'order_id': 'Order_ID',
            'orderid': 'Order_ID', 
            'invoice': 'Order_ID',
            'invoiceno': 'Order_ID',
            'transaction_id': 'Order_ID',
            
            # 产品相关
            'product': 'Product',
            'product_name': 'Product',
            'description': 'Product',
            'stockcode': 'Product',
            'item': 'Product',
            
            # 数量相关
            'quantity': 'Quantity',
            'qty': 'Quantity',
            'amount': 'Quantity',
            
            # 价格相关
            'price': 'Price',
            'unit_price': 'Price',
            'unitprice': 'Price',
            'cost': 'Price',
            
            # 日期相关
            'date': 'Order_Date',
            'order_date': 'Order_Date',
            'invoicedate': 'Order_Date',
            'transaction_date': 'Order_Date',
            
            # 地区相关
            'region': 'Region',
            'country': 'Region',
            'location': 'Region',
            'area': 'Region',
            
            # 客户相关
            'customer': 'Customer_ID',
            'customer_id': 'Customer_ID',
            'customerid': 'Customer_ID',
        }
        
        # 转换列名为小写进行映射
        df_copy = df.copy()
        original_columns = df_copy.columns.tolist()
        
        # 创建新的列名映射
        new_columns = {}
        for col in original_columns:
            col_lower = col.lower().strip()
            if col_lower in column_mapping:
                new_columns[col] = column_mapping[col_lower]
            else:
                new_columns[col] = col
                
        df_copy.rename(columns=new_columns, inplace=True)
        
        # 添加文件来源标识
        df_copy['Source_File'] = file_name
        
        return df_copy, new_columns
    
    def basic_data_cleaning(self, df):
        """基础数据清洗 - 按照项目需求实现完整的数据清洗流程"""
        df_clean = df.copy()
        print(f"    ├─ 开始数据清洗...")
        print(f"       ├─ 清洗前行数: {len(df_clean)}")
        
        # 检查是否为销售数据
        required_cols = ['Order_ID', 'Product', 'Quantity', 'Price', 'Order_Date', 'Region']
        has_sales_data = all(col in df_clean.columns for col in required_cols)
        
        if has_sales_data:
            print(f"       ├─ 识别为销售数据，执行完整清洗流程")
            
            # 1. 处理Price缺失值 - 用中位数填充
            price_missing_before = df_clean['Price'].isnull().sum()
            if price_missing_before > 0:
                price_median = df_clean['Price'].median()
                df_clean['Price'].fillna(price_median, inplace=True)
                print(f"       ├─ Price列缺失值: {price_missing_before} -> 0 (用中位数 {price_median:.2f} 填充)")
            
            # 2. 处理Region缺失值 - 用"Unknown"填充
            region_missing_before = df_clean['Region'].isnull().sum()
            if region_missing_before > 0:
                df_clean['Region'].fillna('Unknown', inplace=True)
                print(f"       ├─ Region列缺失值: {region_missing_before} -> 0 (用'Unknown'填充)")
            
            # 3. 删除完全重复的行
            rows_before = len(df_clean)
            df_clean.drop_duplicates(inplace=True)
            rows_after = len(df_clean)
            print(f"       ├─ 删除重复行: {rows_before} -> {rows_after} (删除 {rows_before - rows_after} 行)")
            
            # 4. 处理日期列
            try:
                df_clean['Order_Date'] = pd.to_datetime(df_clean['Order_Date'], errors='coerce')
                print(f"       ├─ Order_Date列已转换为日期格式")
            except Exception as e:
                print(f"       ├─ 日期转换警告: {e}")
            
            # 5. 异常值处理 - IQR方法处理Quantity列
            Q1 = df_clean['Quantity'].quantile(0.25)
            Q3 = df_clean['Quantity'].quantile(0.75)
            IQR = Q3 - Q1
            upper_bound = Q3 + 1.5 * IQR
            
            outliers_before = len(df_clean[df_clean['Quantity'] > upper_bound])
            df_clean.loc[df_clean['Quantity'] > upper_bound, 'Quantity'] = upper_bound
            outliers_after = len(df_clean[df_clean['Quantity'] > upper_bound])
            print(f"       ├─ Quantity异常值处理: {outliers_before} -> {outliers_after} (上界: {upper_bound:.2f})")
            
            # 6. 创建Sales列
            df_clean['Sales'] = df_clean['Quantity'] * df_clean['Price']
            print(f"       ├─ 已创建Sales列 (Quantity × Price)")
            
            # 7. 确保数值类型正确
            numeric_columns = ['Quantity', 'Price', 'Sales']
            for col in numeric_columns:
                if col in df_clean.columns:
                    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        else:
            print(f"       ├─ 非销售数据，执行基础清洗")
            # 基础清洗逻辑
            # 尝试处理日期列
            date_columns = ['Order_Date', 'date', 'Date']
            for col in date_columns:
                if col in df_clean.columns:
                    try:
                        df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
                    except:
                        pass
            
            # 尝试处理数值列
            numeric_columns = ['Quantity', 'Price', 'Sales']
            for col in numeric_columns:
                if col in df_clean.columns:
                    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        print(f"       └─ 数据清洗完成，最终行数: {len(df_clean)}")
        return df_clean
    
    def process_single_file(self, file_path):
        """处理单个文件"""
        try:
            print(f"    ┌─ 开始处理单个文件: {Path(file_path).name}")
            
            # 加载文件
            print(f"    ├─ 正在加载文件...")
            df = self.load_file(file_path)
            file_name = Path(file_path).name
            print(f"    ├─ 文件加载完成，原始数据: {len(df)} 行 x {len(df.columns)} 列")
            
            # 标准化列名
            print(f"    ├─ 正在标准化列名...")
            df_std, column_mapping = self.standardize_columns(df, file_name)
            mapped_columns = [k for k, v in column_mapping.items() if k != v]
            if mapped_columns:
                print(f"    ├─ 已映射列名: {len(mapped_columns)} 个")
            else:
                print(f"    ├─ 无需映射列名")
            
            # 基础清洗
            print(f"    ├─ 正在进行数据清洗...")
            df_clean = self.basic_data_cleaning(df_std)
            
            # 检查是否为销售数据并生成可视化
            required_cols = ['Order_ID', 'Product', 'Quantity', 'Price', 'Order_Date', 'Region']
            has_sales_data = all(col in df_clean.columns for col in required_cols)
            
            visualization_files = []
            if has_sales_data and 'Sales' in df_clean.columns:
                print(f"    ├─ 检测到销售数据，生成可视化图表...")
                visualization_files = self.generate_sales_visualization(df_clean)
            
            # 检查Sales列
            if 'Sales' in df_clean.columns:
                sales_count = df_clean['Sales'].notna().sum()
                total_sales = df_clean['Sales'].sum()
                print(f"    ├─ 销售数据: {sales_count} 条有效记录，总额: {total_sales:,.2f}")
            else:
                print(f"    ├─ 未找到销售数据列")
            
            # 生成文件摘要
            print(f"    ├─ 正在生成文件摘要...")
            summary = self.generate_file_summary(df_clean, file_name)
            
            # 添加可视化文件信息到摘要
            if visualization_files:
                summary['visualization_files'] = visualization_files
            
            # 存储处理结果
            self.processed_files[file_name] = {
                'original_data': df,
                'processed_data': df_clean,
                'column_mapping': column_mapping,
                'summary': summary,
                'file_path': file_path,
                'visualization_files': visualization_files
            }
            
            print(f"    └─ 单个文件处理完成")
            
            return df_clean, summary
            
        except Exception as e:
            print(f"    └─ 单个文件处理失败: {str(e)}")
            raise Exception(f"处理文件失败 {file_path}: {str(e)}")
    
    def generate_file_summary(self, df, file_name):
        """生成文件摘要统计 - 增强销售数据分析"""
        summary = {
            'file_name': file_name,
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': df.columns.tolist(),
            'missing_values': df.isnull().sum().to_dict(),
            'data_types': df.dtypes.to_dict()
        }
        
        # 检查是否为销售数据
        required_cols = ['Order_ID', 'Product', 'Quantity', 'Price', 'Order_Date', 'Region']
        has_sales_data = all(col in df.columns for col in required_cols)
        summary['is_sales_data'] = has_sales_data
        
        if has_sales_data:
            print(f"    ├─ 生成销售数据分析摘要...")
            
            # 销售额统计
            if 'Sales' in df.columns:
                summary['total_sales'] = float(df['Sales'].sum())
                summary['avg_sales'] = float(df['Sales'].mean())
                summary['median_sales'] = float(df['Sales'].median())
                summary['max_sales'] = float(df['Sales'].max())
                summary['min_sales'] = float(df['Sales'].min())
                print(f"       ├─ 总销售额: {summary['total_sales']:,.2f}")
                print(f"       ├─ 平均销售额: {summary['avg_sales']:,.2f}")
            
            # 地区统计
            if 'Region' in df.columns:
                region_stats = df.groupby('Region').agg({
                    'Sales': ['sum', 'count', 'mean'] if 'Sales' in df.columns else 'count'
                }).round(2)
                
                if 'Sales' in df.columns:
                    region_stats.columns = ['总销售额', '订单数', '平均订单金额']
                    summary['region_analysis'] = region_stats.to_dict('index')
                    print(f"       ├─ 地区分析完成，共 {len(region_stats)} 个地区")
                
            # 产品统计 - 增强错误处理
            if 'Product' in df.columns:
                try:
                    # 检查Product列是否有效数据
                    valid_products = df['Product'].notna()
                    if valid_products.sum() > 0:
                        # 清理Product列数据
                        df_clean_products = df[valid_products].copy()
                        
                        # 确保Product列是字符串类型
                        df_clean_products['Product'] = df_clean_products['Product'].astype(str)
                        
                        # 移除空字符串和"nan"字符串 - 修复布尔判断错误
                        # 分步进行条件筛选以避免Series布尔判断错误
                        mask1 = df_clean_products['Product'] != ''
                        mask2 = df_clean_products['Product'] != 'nan'
                        mask3 = df_clean_products['Product'] != 'None'
                        
                        # 组合所有条件
                        combined_mask = mask1 & mask2 & mask3
                        df_clean_products = df_clean_products[combined_mask]
                        
                        if len(df_clean_products) > 0:
                            # 重置索引以避免groupby问题
                            df_clean_products = df_clean_products.reset_index(drop=True)
                            
                            # 进行产品分组统计
                            if 'Sales' in df.columns:
                                product_stats = df_clean_products.groupby('Product', as_index=False).agg({
                                    'Sales': ['sum', 'count']
                                }).round(2)
                                
                                # 重新命名列
                                product_stats.columns = ['Product', '总销售额', '订单数']
                                product_stats = product_stats.set_index('Product')
                                
                                # 只保存前10个产品
                                top_products = product_stats.sort_values('总销售额', ascending=False).head(10)
                                summary['top_products'] = top_products.to_dict('index')
                                print(f"       ├─ 产品分析完成，共 {len(product_stats)} 个产品")
                            else:
                                product_count = df_clean_products.groupby('Product', as_index=False).size()
                                print(f"       ├─ 产品分析完成，共 {len(product_count)} 个产品（无销售数据）")
                        else:
                            print(f"       ├─ 产品列清理后无有效数据，跳过产品分析")
                    else:
                        print(f"       ├─ 产品列为空，跳过产品分析")
                        
                except Exception as e:
                    print(f"       ├─ 产品分析错误: {str(e)}")
                    print(f"       ├─ 跳过产品分析，继续处理其他统计")
                    # 继续处理，不中断流程
            
            # 时间维度分析
            if 'Order_Date' in df.columns:
                try:
                    date_col = pd.to_datetime(df['Order_Date'], errors='coerce')
                    valid_dates = date_col.dropna()
                    if len(valid_dates) > 0:
                        summary['date_range'] = {
                            'start': valid_dates.min().strftime('%Y-%m-%d'),
                            'end': valid_dates.max().strftime('%Y-%m-%d')
                        }
                        print(f"       ├─ 日期范围: {summary['date_range']['start']} ~ {summary['date_range']['end']}")
                except Exception as e:
                    print(f"       ├─ 日期分析警告: {e}")
        else:
            print(f"    ├─ 生成基础数据摘要...")
            # 数值统计
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                summary['numeric_summary'] = df[numeric_cols].describe().to_dict()
        
        return summary
    
    def generate_sales_visualization(self, df, output_dir="outputs"):
        """生成销售数据可视化图表"""
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as fm
        
        # 检查是否为销售数据
        required_cols = ['Region', 'Sales']
        if not all(col in df.columns for col in required_cols):
            print(f"    ├─ 跳过图表生成：缺少必要的销售数据列")
            return []
        
        print(f"    ├─ 开始生成销售数据可视化图表...")
        
        # 配置中文字体
        try:
            chinese_fonts = ['Microsoft YaHei', 'SimHei', 'SimSun', 'FangSong']
            available_fonts = [f.name for f in fm.fontManager.ttflist]
            
            for font in chinese_fonts:
                if font in available_fonts:
                    plt.rcParams['font.sans-serif'] = [font]
                    plt.rcParams['axes.unicode_minus'] = False
                    break
            else:
                plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
                plt.rcParams['axes.unicode_minus'] = False
        except Exception as e:
            print(f"       ├─ 字体配置警告: {e}")
        
        # 确保输出目录存在
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        generated_files = []
        
        try:
            # 1. 各地区总销售额柱状图
            plt.figure(figsize=(12, 8))
            region_sales = df.groupby('Region')['Sales'].sum().sort_values(ascending=False)
            
            bars = plt.bar(region_sales.index, region_sales.values, 
                          color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'],
                          alpha=0.8, edgecolor='black', linewidth=1)
            
            plt.title('各地区总销售额 (Total Sales by Region)', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('地区 (Region)', fontsize=12, fontweight='bold')
            plt.ylabel('总销售额 (Total Sales)', fontsize=12, fontweight='bold')
            plt.xticks(rotation=45, ha='right')
            plt.grid(True, alpha=0.3, axis='y')
            
            # 添加数值标签
            for i, (region, value) in enumerate(region_sales.items()):
                plt.text(i, value + max(region_sales.values) * 0.01, 
                        f'{value:,.0f}', ha='center', va='bottom', 
                        fontweight='bold', fontsize=10)
            
            plt.tight_layout()
            chart_file = f"{output_dir}/sales_by_region.png"
            plt.savefig(chart_file, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            generated_files.append(chart_file)
            print(f"       ├─ 生成柱状图: {chart_file}")
            
            # 2. 综合分析图表
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('销售数据综合分析 (Comprehensive Sales Analysis)', 
                        fontsize=16, fontweight='bold', y=0.98)
            
            # 2.1 各地区销售额分布
            region_sales.plot(kind='bar', ax=axes[0, 0], color='skyblue', alpha=0.8)
            axes[0, 0].set_title('各地区总销售额 (Total Sales by Region)', fontweight='bold')
            axes[0, 0].set_xlabel('地区 (Region)')
            axes[0, 0].set_ylabel('总销售额 (Total Sales)')
            axes[0, 0].tick_params(axis='x', rotation=45)
            axes[0, 0].grid(True, alpha=0.3)
            
            # 2.2 销售额分布直方图
            axes[0, 1].hist(df['Sales'], bins=30, color='lightcoral', alpha=0.7, edgecolor='black')
            axes[0, 1].set_title('销售额分布 (Sales Distribution)', fontweight='bold')
            axes[0, 1].set_xlabel('销售额 (Sales Amount)')
            axes[0, 1].set_ylabel('频次 (Frequency)')
            axes[0, 1].grid(True, alpha=0.3)
            
            # 2.3 产品销售额前10
            if 'Product' in df.columns:
                try:
                    # 检查Product列是否有效
                    valid_products = df['Product'].notna()
                    if valid_products.sum() > 0:
                        # 清理Product列数据
                        df_clean_products = df[valid_products].copy()
                        
                        # 确保Product列是字符串类型
                        df_clean_products['Product'] = df_clean_products['Product'].astype(str)
                        
                        # 移除空字符串和"nan"字符串 - 修复布尔判断错误
                        # 分步进行条件筛选以避免Series布尔判断错误
                        mask1 = df_clean_products['Product'] != ''
                        mask2 = df_clean_products['Product'] != 'nan'
                        mask3 = df_clean_products['Product'] != 'None'
                        
                        # 组合所有条件
                        combined_mask = mask1 & mask2 & mask3
                        df_clean_products = df_clean_products[combined_mask]
                        
                        if len(df_clean_products) > 0 and 'Sales' in df_clean_products.columns:
                            # 重置索引以避免groupby问题
                            df_clean_products = df_clean_products.reset_index(drop=True)
                            
                            # 进行产品分组统计
                            product_sales = df_clean_products.groupby('Product', as_index=False)['Sales'].sum()
                            product_sales = product_sales.sort_values('Sales', ascending=False).head(10)
                            
                            if len(product_sales) > 0:
                                # 创建水平条形图
                                y_pos = range(len(product_sales))
                                axes[1, 0].barh(y_pos, product_sales['Sales'], 
                                               color='lightgreen', alpha=0.8)
                                axes[1, 0].set_yticks(y_pos)
                                axes[1, 0].set_yticklabels(product_sales['Product'], fontsize=9)
                                axes[1, 0].set_title('销售额最高的前10个产品 (Top 10 Products by Sales)', fontweight='bold')
                                axes[1, 0].set_xlabel('总销售额 (Total Sales)')
                                axes[1, 0].grid(True, alpha=0.3, axis='x')
                            else:
                                # 如果没有产品数据，显示占位图
                                axes[1, 0].text(0.5, 0.5, '无产品数据\n(No Product Data)', 
                                               transform=axes[1, 0].transAxes, ha='center', va='center',
                                               fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
                                axes[1, 0].set_title('产品销售分析 (Product Sales Analysis)', fontweight='bold')
                        else:
                            # 如果清理后没有有效数据
                            axes[1, 0].text(0.5, 0.5, '产品数据无效\n(Invalid Product Data)', 
                                           transform=axes[1, 0].transAxes, ha='center', va='center',
                                           fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
                            axes[1, 0].set_title('产品销售分析 (Product Sales Analysis)', fontweight='bold')
                    else:
                        # Product列全为空值
                        axes[1, 0].text(0.5, 0.5, '产品列为空\n(Product Column Empty)', 
                                       transform=axes[1, 0].transAxes, ha='center', va='center',
                                       fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
                        axes[1, 0].set_title('产品销售分析 (Product Sales Analysis)', fontweight='bold')
                        
                except Exception as e:
                    print(f"       ├─ 产品分析警告: {str(e)}")
                    # 显示错误信息
                    axes[1, 0].text(0.5, 0.5, f'产品分析错误\n{str(e)[:50]}...', 
                                   transform=axes[1, 0].transAxes, ha='center', va='center',
                                   fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral"))
                    axes[1, 0].set_title('产品销售分析 (Product Sales Analysis)', fontweight='bold')
            else:
                # 没有Product列
                axes[1, 0].text(0.5, 0.5, '缺少产品列\n(Missing Product Column)', 
                               transform=axes[1, 0].transAxes, ha='center', va='center',
                               fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
                axes[1, 0].set_title('产品销售分析 (Product Sales Analysis)', fontweight='bold')
            
            # 2.4 订单数量vs销售额散点图
            region_summary = df.groupby('Region').agg({'Sales': 'sum', 'Order_ID': 'count'})
            scatter = axes[1, 1].scatter(region_summary['Order_ID'], region_summary['Sales'], 
                                       s=120, alpha=0.7, color='orange', edgecolors='black')
            for i, region in enumerate(region_summary.index):
                axes[1, 1].annotate(region, 
                                   (region_summary['Order_ID'].iloc[i], region_summary['Sales'].iloc[i]),
                                   xytext=(5, 5), textcoords='offset points', fontsize=9, fontweight='bold')
            axes[1, 1].set_title('订单数量 vs 总销售额 (Order Count vs Total Sales)', fontweight='bold')
            axes[1, 1].set_xlabel('订单数量 (Order Count)')
            axes[1, 1].set_ylabel('总销售额 (Total Sales)')
            axes[1, 1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            comprehensive_file = f"{output_dir}/comprehensive_analysis.png"
            plt.savefig(comprehensive_file, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            generated_files.append(comprehensive_file)
            print(f"       ├─ 生成综合分析图: {comprehensive_file}")
            
        except Exception as e:
            print(f"       ├─ 图表生成警告: {e}")
        
        print(f"    └─ 图表生成完成，共生成 {len(generated_files)} 个文件")
        return generated_files

    def generate_analysis_report(self, output_dir="outputs"):
        """生成完整的销售数据分析报告"""
        if not self.processed_files:
            print("没有已处理的文件数据")
            return None
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # 合并所有销售数据
        sales_files = []
        for file_name, file_data in self.processed_files.items():
            if file_data['summary'].get('is_sales_data', False):
                sales_files.append((file_name, file_data))
        
        if not sales_files:
            print("没有发现销售数据文件")
            return None
        
        print(f"开始生成分析报告，共 {len(sales_files)} 个销售数据文件")
        
        # 创建报告内容
        report_content = []
        report_content.append("# 销售数据分析报告 (Sales Data Analysis Report)")
        report_content.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_content.append("")
        report_content.append("## 数据概览 (Data Overview)")
        
        total_records = 0
        total_sales = 0
        all_regions = set()
        all_products = set()
        
        for file_name, file_data in sales_files:
            summary = file_data['summary']
            total_records += summary['total_rows']
            total_sales += summary.get('total_sales', 0)
            
            # 收集地区和产品信息
            if 'region_analysis' in summary:
                all_regions.update(summary['region_analysis'].keys())
            if 'top_products' in summary:
                all_products.update(summary['top_products'].keys())
        
        report_content.append(f"- 总记录数: {total_records:,}")
        report_content.append(f"- 总销售额: {total_sales:,.2f}")
        report_content.append(f"- 涉及地区: {len(all_regions)} 个")
        report_content.append(f"- 涉及产品: {len(all_products)} 个")
        report_content.append("")
        
        # 详细分析每个文件
        for i, (file_name, file_data) in enumerate(sales_files, 1):
            summary = file_data['summary']
            report_content.append(f"## 文件 {i}: {file_name}")
            report_content.append("")
            
            # 基本信息
            report_content.append("### 基本信息 (Basic Information)")
            report_content.append(f"- 数据行数: {summary['total_rows']:,}")
            report_content.append(f"- 数据列数: {summary['total_columns']}")
            report_content.append(f"- 总销售额: {summary.get('total_sales', 0):,.2f}")
            report_content.append(f"- 平均销售额: {summary.get('avg_sales', 0):,.2f}")
            if 'date_range' in summary:
                report_content.append(f"- 日期范围: {summary['date_range']['start']} ~ {summary['date_range']['end']}")
            report_content.append("")
            
            # 地区分析
            if 'region_analysis' in summary:
                report_content.append("### 地区分析 (Regional Analysis)")
                region_data = summary['region_analysis']
                for region, stats in region_data.items():
                    report_content.append(f"- **{region}**: 总销售额 {stats['总销售额']:,.2f}, 订单数 {stats['订单数']}, 平均订单金额 {stats['平均订单金额']:,.2f}")
                report_content.append("")
            
            # 产品分析
            if 'top_products' in summary:
                report_content.append("### 热销产品 (Top Products)")
                product_data = summary['top_products']
                for product, stats in list(product_data.items())[:5]:  # 只显示前5个
                    report_content.append(f"- **{product}**: 总销售额 {stats['总销售额']:,.2f}, 订单数 {stats['订单数']}")
                report_content.append("")
            
            # 可视化文件
            if 'visualization_files' in summary and summary['visualization_files']:
                report_content.append("### 生成的图表 (Generated Charts)")
                for chart_file in summary['visualization_files']:
                    chart_name = os.path.basename(chart_file)
                    report_content.append(f"- {chart_name}")
                report_content.append("")
        
        # 业务见解
        report_content.append("## 业务见解 (Business Insights)")
        report_content.append("")
        report_content.append("### 主要发现 (Key Findings)")
        
        # 地区分析见解
        if sales_files:
            all_region_data = {}
            for file_name, file_data in sales_files:
                if 'region_analysis' in file_data['summary']:
                    for region, stats in file_data['summary']['region_analysis'].items():
                        if region not in all_region_data:
                            all_region_data[region] = {'总销售额': 0, '订单数': 0}
                        all_region_data[region]['总销售额'] += stats['总销售额']
                        all_region_data[region]['订单数'] += stats['订单数']
            
            if all_region_data:
                # 找出最佳地区
                best_region = max(all_region_data.items(), key=lambda x: x[1]['总销售额'])
                report_content.append(f"1. **最佳销售地区**: {best_region[0]}，总销售额为 {best_region[1]['总销售额']:,.2f}")
                
                # 计算地区分布
                total_region_sales = sum(data['总销售额'] for data in all_region_data.values())
                best_region_percentage = (best_region[1]['总销售额'] / total_region_sales) * 100
                report_content.append(f"   - 占总销售额的 {best_region_percentage:.1f}%")
                
                # 找出订单数最多的地区
                most_orders_region = max(all_region_data.items(), key=lambda x: x[1]['订单数'])
                if most_orders_region[0] != best_region[0]:
                    report_content.append(f"2. **订单数最多地区**: {most_orders_region[0]}，共 {most_orders_region[1]['订单数']} 个订单")
                
                # 平均订单金额分析
                avg_order_values = {region: data['总销售额'] / data['订单数'] 
                                  for region, data in all_region_data.items() if data['订单数'] > 0}
                if avg_order_values:
                    best_avg_region = max(avg_order_values.items(), key=lambda x: x[1])
                    report_content.append(f"3. **平均订单金额最高地区**: {best_avg_region[0]}，平均 {best_avg_region[1]:,.2f}")
        
        report_content.append("")
        report_content.append("### 建议 (Recommendations)")
        report_content.append("1. 加强在高销售额地区的市场投入，巩固市场地位")
        report_content.append("2. 分析低销售额地区的原因，制定针对性的改进策略")
        report_content.append("3. 研究高平均订单金额地区的成功因素，推广到其他地区")
        report_content.append("4. 优化产品结构，重点推广热销产品")
        report_content.append("")
        
        # 保存报告
        report_file = f"{output_dir}/sales_analysis_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_content))
        
        print(f"分析报告已保存到: {report_file}")
        return report_file
    
    def process_multiple_files(self, file_paths, progress_callback=None):
        """批量处理多个文件"""
        print(f"\n🚀 开始批量处理 {len(file_paths)} 个文件")
        
        results = {}
        total_files = len(file_paths)
        
        for i, file_path in enumerate(file_paths, 1):
            try:
                if progress_callback:
                    progress_callback(i-1, total_files, f"正在处理文件 {i}/{total_files}: {Path(file_path).name}")
                
                print(f"\n📄 处理文件 {i}/{total_files}: {Path(file_path).name}")
                
                # 处理单个文件
                df_processed, summary = self.process_single_file(file_path)
                
                results[Path(file_path).name] = {
                    'success': True,
                    'data': df_processed,
                    'summary': summary,
                    'file_path': file_path
                }
                
                print(f"✅ 文件 {i} 处理成功")
                
            except Exception as e:
                print(f"❌ 文件 {i} 处理失败: {str(e)}")
                results[Path(file_path).name] = {
                    'success': False,
                    'error': str(e),
                    'file_path': file_path
                }
        
        if progress_callback:
            progress_callback(total_files, total_files, "所有文件处理完成")
        
        print(f"\n✅ 批量处理完成，成功处理 {sum(1 for r in results.values() if r.get('success', False))}/{total_files} 个文件")
        return results
    
    def combine_all_data(self):
        """合并所有已处理的数据"""
        if not self.processed_files:
            print("没有已处理的数据可以合并")
            return None
        
        print(f"\n🔗 开始合并数据，共 {len(self.processed_files)} 个文件")
        
        combined_data_list = []
        
        for file_name, file_data in self.processed_files.items():
            if file_data.get('success', True):  # 兼容不同的数据结构
                # 获取处理后的数据
                if 'processed_data' in file_data:
                    df = file_data['processed_data']
                elif 'data' in file_data:
                    df = file_data['data']
                else:
                    print(f"⚠️ 跳过文件 {file_name}：找不到处理后的数据")
                    continue
                
                if df is not None and len(df) > 0:
                    # 创建数据副本以避免修改原始数据
                    df_copy = df.copy()
                    
                    # 重置索引以避免索引冲突
                    df_copy = df_copy.reset_index(drop=True)
                    
                    # 确保列名唯一且一致
                    if df_copy.columns.duplicated().any():
                        print(f"   ├─ 修复文件 {file_name} 的重复列名")
                        # 为重复列名添加后缀
                        cols = df_copy.columns.tolist()
                        seen = set()
                        for i, col in enumerate(cols):
                            if col in seen:
                                counter = 1
                                new_col = f"{col}_{counter}"
                                while new_col in seen:
                                    counter += 1
                                    new_col = f"{col}_{counter}"
                                cols[i] = new_col
                            seen.add(cols[i])
                        df_copy.columns = cols
                    
                    combined_data_list.append(df_copy)
                    print(f"   ├─ 添加文件: {file_name} ({len(df_copy)} 行, {len(df_copy.columns)} 列)")
                else:
                    print(f"   ├─ 跳过空文件: {file_name}")
        
        if not combined_data_list:
            print("没有有效数据可以合并")
            return None
        
        try:
            # 检查所有DataFrame的列结构
            all_columns = set()
            for df in combined_data_list:
                all_columns.update(df.columns)
            
            print(f"   ├─ 发现总共 {len(all_columns)} 个唯一列名")
            
            # 统一列结构 - 为每个DataFrame添加缺失的列
            standardized_dfs = []
            for i, df in enumerate(combined_data_list):
                df_std = df.copy()
                
                # 添加缺失的列（用NaN填充）
                missing_cols = all_columns - set(df.columns)
                for col in missing_cols:
                    df_std[col] = np.nan
                
                # 重新排序列以保持一致性
                df_std = df_std.reindex(columns=sorted(all_columns))
                standardized_dfs.append(df_std)
            
            # 合并数据
            self.combined_data = pd.concat(standardized_dfs, ignore_index=True, sort=False)
            print(f"✅ 数据合并完成，合并后总行数: {len(self.combined_data)}")
            print(f"   └─ 合并后列数: {len(self.combined_data.columns)}")
            
        except Exception as e:
            print(f"❌ 数据合并失败: {str(e)}")
            print(f"   └─ 尝试使用备用合并方法...")
            
            try:
                # 备用方法：只合并具有相同列结构的数据
                grouped_by_columns = {}
                for i, df in enumerate(combined_data_list):
                    col_signature = tuple(sorted(df.columns))
                    if col_signature not in grouped_by_columns:
                        grouped_by_columns[col_signature] = []
                    grouped_by_columns[col_signature].append(df)
                
                # 分别合并每组
                merged_groups = []
                for col_signature, df_group in grouped_by_columns.items():
                    if len(df_group) > 1:
                        group_merged = pd.concat(df_group, ignore_index=True)
                        print(f"   ├─ 合并列结构组 {len(col_signature)} 列: {len(df_group)} 个文件")
                    else:
                        group_merged = df_group[0]
                        print(f"   ├─ 单个文件组 {len(col_signature)} 列: 1 个文件")
                    merged_groups.append(group_merged)
                
                # 最终合并所有组（使用outer join）
                if len(merged_groups) == 1:
                    self.combined_data = merged_groups[0]
                else:
                    # 使用外连接合并不同结构的数据
                    self.combined_data = merged_groups[0]
                    for df in merged_groups[1:]:
                        # 找到共同列
                        common_cols = list(set(self.combined_data.columns) & set(df.columns))
                        if common_cols:
                            print(f"   ├─ 基于 {len(common_cols)} 个共同列合并")
                            # 只保留共同列进行合并
                            df1_common = self.combined_data[common_cols].copy()
                            df2_common = df[common_cols].copy()
                            self.combined_data = pd.concat([df1_common, df2_common], ignore_index=True)
                        else:
                            print(f"   ├─ 无共同列，分别保存")
                            # 如果没有共同列，添加所有列并用NaN填充
                            all_cols = list(set(self.combined_data.columns) | set(df.columns))
                            
                            # 为第一个DataFrame添加缺失列
                            for col in df.columns:
                                if col not in self.combined_data.columns:
                                    self.combined_data[col] = np.nan
                            
                            # 为第二个DataFrame添加缺失列
                            df_extended = df.copy()
                            for col in self.combined_data.columns:
                                if col not in df_extended.columns:
                                    df_extended[col] = np.nan
                            
                            # 重新排序列
                            self.combined_data = self.combined_data.reindex(columns=all_cols)
                            df_extended = df_extended.reindex(columns=all_cols)
                            
                            # 合并
                            self.combined_data = pd.concat([self.combined_data, df_extended], ignore_index=True)
                
                print(f"✅ 备用方法合并成功，合并后总行数: {len(self.combined_data)}")
                print(f"   └─ 合并后列数: {len(self.combined_data.columns)}")
                
            except Exception as backup_error:
                print(f"❌ 备用合并方法也失败: {str(backup_error)}")
                print(f"   └─ 返回空结果")
                return None
        
        return self.combined_data
    
    def save_results(self, output_dir="outputs", separate_files=True, combined_file=True):
        """保存处理结果"""
        import os
        from datetime import datetime
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n💾 开始保存结果到目录: {output_dir}")
        print(f"保存设置: 单独文件={separate_files}, 合并文件={combined_file}")
        
        saved_files = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存单独的处理文件
        if separate_files and self.processed_files:
            print(f"   ├─ 保存单独处理文件...")
            
            for file_name, file_data in self.processed_files.items():
                if file_data.get('success', True):
                    # 获取处理后的数据
                    if 'processed_data' in file_data:
                        df = file_data['processed_data']
                    elif 'data' in file_data:
                        df = file_data['data']
                    else:
                        continue
                    
                    if df is not None and len(df) > 0:
                        # 生成输出文件名
                        base_name = Path(file_name).stem
                        output_file = f"{output_dir}/{base_name}_processed_{timestamp}.csv"
                        
                        # 保存文件
                        df.to_csv(output_file, index=False, encoding='utf-8-sig')
                        saved_files.append(output_file)
                        
                        file_size = os.path.getsize(output_file) / 1024  # KB
                        print(f"      ├─ 保存文件: {output_file} ({file_size:.1f} KB)")
        
        # 保存合并文件
        if combined_file and self.combined_data is not None:
            print(f"   ├─ 保存合并文件...")
            combined_output_file = f"{output_dir}/combined_data_{timestamp}.csv"
            self.combined_data.to_csv(combined_output_file, index=False, encoding='utf-8-sig')
            saved_files.append(combined_output_file)
            
            file_size = os.path.getsize(combined_output_file) / 1024  # KB
            print(f"      ├─ 保存合并文件: {combined_output_file} ({file_size:.1f} KB)")
        
        # 保存处理摘要
        if self.processed_files:
            print(f"   ├─ 保存处理摘要...")
            summary_data = []
            
            for file_name, file_data in self.processed_files.items():
                if file_data.get('success', True):
                    summary = file_data.get('summary', {})
                    summary_data.append({
                        'file_name': file_name,
                        'total_rows': summary.get('total_rows', 0),
                        'total_columns': summary.get('total_columns', 0),
                        'is_sales_data': summary.get('is_sales_data', False),
                        'total_sales': summary.get('total_sales', 0),
                        'avg_sales': summary.get('avg_sales', 0)
                    })
            
            if summary_data:
                summary_df = pd.DataFrame(summary_data)
                summary_file = f"{output_dir}/processing_summary_{timestamp}.csv"
                summary_df.to_csv(summary_file, index=False, encoding='utf-8-sig')
                saved_files.append(summary_file)
                
                file_size = os.path.getsize(summary_file) / 1024  # KB
                print(f"      ├─ 保存摘要文件: {summary_file} ({file_size:.1f} KB)")
        
        # 生成分析报告（如果有销售数据）
        has_sales_data = any(
            file_data.get('summary', {}).get('is_sales_data', False) 
            for file_data in self.processed_files.values() 
            if file_data.get('success', True)
        )
        
        if has_sales_data:
            print(f"   ├─ 生成分析报告...")
            try:
                report_file = self.generate_analysis_report(output_dir)
                if report_file:
                    saved_files.append(report_file)
                    file_size = os.path.getsize(report_file) / 1024  # KB
                    print(f"      ├─ 保存分析报告: {report_file} ({file_size:.1f} KB)")
            except Exception as e:
                print(f"      ├─ 生成分析报告时出错: {str(e)}")
        
        print(f"✅ 结果保存完成，共保存 {len(saved_files)} 个文件")
        
        # 显示保存结果摘要
        total_size = sum(os.path.getsize(f) / 1024 for f in saved_files if os.path.exists(f))
        print(f"   └─ 文件总大小: {total_size:.1f} KB")
        
        return saved_files
    
    def generate_combined_report(self):
        """生成综合报告（用于GUI）"""
        if not self.processed_files:
            return {}
        
        # 统计信息
        total_files = len(self.processed_files)
        success_files = sum(1 for r in self.processed_files.values() if r.get('success', True))
        total_records = 0
        total_sales = 0
        
        # 收集地区和产品信息
        all_regions = {}
        all_products = {}
        file_breakdown = {}
        
        for file_name, file_data in self.processed_files.items():
            if file_data.get('success', True):
                summary = file_data.get('summary', {})
                
                # 基本统计
                records = summary.get('total_rows', 0)
                sales = summary.get('total_sales', 0)
                total_records += records
                total_sales += sales
                
                # 文件分解
                file_breakdown[file_name] = {
                    '记录数': records,
                    '销售额': sales,
                    '是否销售数据': summary.get('is_sales_data', False)
                }
                
                # 地区统计
                if 'region_analysis' in summary:
                    for region, stats in summary['region_analysis'].items():
                        if region not in all_regions:
                            all_regions[region] = 0
                        all_regions[region] += stats.get('总销售额', 0)
                
                # 产品统计
                if 'top_products' in summary:
                    for product, stats in summary['top_products'].items():
                        if product not in all_products:
                            all_products[product] = 0
                        all_products[product] += stats.get('总销售额', 0)
        
        # 排序
        top_regions = dict(sorted(all_regions.items(), key=lambda x: x[1], reverse=True)[:10])
        top_products = dict(sorted(all_products.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # 日期范围
        date_range = None
        if self.combined_data is not None and 'Order_Date' in self.combined_data.columns:
            try:
                dates = pd.to_datetime(self.combined_data['Order_Date'], errors='coerce').dropna()
                if len(dates) > 0:
                    date_range = {
                        'start': dates.min().strftime('%Y-%m-%d'),
                        'end': dates.max().strftime('%Y-%m-%d')
                    }
            except:
                pass
        
        return {
            'total_files_processed': success_files,
            'total_records': total_records,
            'total_sales': total_sales,
            'avg_order_value': total_sales / total_records if total_records > 0 else 0,
            'top_regions': top_regions,
            'top_products': top_products,
            'file_breakdown': file_breakdown,
            'date_range': date_range
        } 