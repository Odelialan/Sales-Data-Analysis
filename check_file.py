#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

try:
    print("正在加载 Online Retail.xlsx...")
    df = pd.read_excel('data/Online Retail.xlsx', nrows=10)
    
    print("列名:", df.columns.tolist())
    print("\n数据类型:")
    print(df.dtypes)
    
    print("\n前5行数据:")
    print(df.head())
    
    print("\n数据维度:", df.shape)
    
    # 检查是否有Product相关列
    product_cols = [col for col in df.columns if 'product' in col.lower() or 'description' in col.lower()]
    print("\n可能的产品列:", product_cols)
    
    # 检查Description列的内容
    if 'Description' in df.columns:
        print("\nDescription列示例:")
        print(df['Description'].head(10).tolist())
        print("Description列是否有重复列名:", df.columns.duplicated().any())
        
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc() 