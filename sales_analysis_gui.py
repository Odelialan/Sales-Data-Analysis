#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
销售数据分析 GUI 应用

基于 Streamlit 的现代化 Web 界面，支持：
- 多文件批量处理
- 交互式可视化
- 自定义数据路径
- 结果导出选项
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from pathlib import Path
from datetime import datetime
import time
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 配置中文字体支持
def setup_chinese_fonts():
    """配置中文字体支持"""
    # matplotlib 字体配置
    try:
        # 尝试使用系统中的中文字体
        chinese_fonts = ['Microsoft YaHei', 'SimHei', 'SimSun', 'FangSong']
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        
        for font in chinese_fonts:
            if font in available_fonts:
                plt.rcParams['font.sans-serif'] = [font]
                plt.rcParams['axes.unicode_minus'] = False
                break
        else:
            # 如果没有找到中文字体，使用默认配置
            plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
            
    except Exception as e:
        print(f"字体配置警告: {e}")

# 初始化字体配置
setup_chinese_fonts()

# 添加 scripts 目录到路径
sys.path.append('scripts')

try:
    from scripts.multi_file_processor import MultiFileProcessor
except ImportError:
    st.error("无法导入 MultiFileProcessor 模块，请确认 scripts/multi_file_processor.py 文件存在")
    st.stop()

# 页面配置
st.set_page_config(
    page_title="销售数据分析系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS 样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
    
    .info-card {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'processor' not in st.session_state:
    st.session_state.processor = MultiFileProcessor()
if 'processed_results' not in st.session_state:
    st.session_state.processed_results = {}
if 'combined_data' not in st.session_state:
    st.session_state.combined_data = None
if 'scanned_files' not in st.session_state:
    st.session_state.scanned_files = []
if 'scan_completed' not in st.session_state:
    st.session_state.scan_completed = False

def main():
    """主函数"""
    
    # 页面标题
    st.markdown('<h1 class="main-header">📊 销售数据分析系统</h1>', unsafe_allow_html=True)
    
    # 侧边栏配置
    with st.sidebar:
        st.header("🔧 配置选项")
        
        # 数据路径设置
        st.subheader("📁 数据路径")
        use_default_path = st.checkbox("使用默认路径 (data/)", value=True)
        
        if use_default_path:
            data_path = "data"
        else:
            data_path = st.text_input("自定义数据路径", value="data", help="输入包含数据文件的目录路径")
        
        # 输出设置
        st.subheader("💾 输出设置")
        save_separate = st.checkbox("保存单独的处理文件", value=True)
        save_combined = st.checkbox("保存合并文件", value=True)
        
        # 可视化设置
        st.subheader("📈 可视化设置")
        chart_theme = st.selectbox("图表主题", ["plotly", "plotly_white", "plotly_dark", "ggplot2"])
        show_data_labels = st.checkbox("显示数据标签", value=True)
        
        # 高级选项
        st.subheader("⚙️ 高级选项")
        max_files = st.number_input("最大处理文件数", min_value=1, max_value=50, value=10)
        chunk_size = st.number_input("大文件分块大小", min_value=1000, max_value=100000, value=10000, step=1000)
    
    # 主内容区域
    tab1, tab2, tab3, tab4 = st.tabs(["📂 文件处理", "📊 数据概览", "📈 可视化分析", "📋 报告导出"])
    
    with tab1:
        file_processing_tab(data_path, max_files, save_separate, save_combined)
    
    with tab2:
        data_overview_tab()
    
    with tab3:
        visualization_tab(chart_theme, show_data_labels)
    
    with tab4:
        report_export_tab()

def file_processing_tab(data_path, max_files, save_separate, save_combined):
    """文件处理标签页"""
    st.header("📂 文件处理")
    
    # 添加文件选择指南
    st.markdown("""
    <div class="info-card">
        <h4>💡 文件选择指南</h4>
        <p><strong>推荐文件:</strong> <code>raw_sales_data.csv</code> - 包含销售分析所需的完整字段</p>
        <p><strong>⚠️ 避免选择:</strong> <code>olist_customers_dataset.csv</code> - 仅包含客户信息，缺少销售数据</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 快速选择推荐文件
    st.subheader("🚀 快速开始")
    col_quick1, col_quick2 = st.columns([2, 1])
    
    with col_quick1:
        # 检查推荐文件是否存在
        recommended_file = os.path.join(data_path, "raw_sales_data.csv")
        if os.path.exists(recommended_file):
            st.success(f"✅ 发现推荐文件: {recommended_file}")
            if st.button("🎯 使用推荐文件进行分析", type="primary", key="quick_process"):
                print(f"\n🎯 GUI: 用户选择快速处理推荐文件")
                
                with st.spinner("正在处理推荐的销售数据文件..."):
                    try:
                        # 直接处理推荐文件
                        result = st.session_state.processor.process_single_file(recommended_file)
                        
                        # process_single_file 返回 (df_clean, summary)
                        if result is not None and len(result) == 2:
                            df_processed, summary = result
                            filename = os.path.basename(recommended_file)
                            
                            # 存储处理结果 - 修正数据结构
                            st.session_state.processed_results[filename] = {
                                'success': True,
                                'data': df_processed,
                                'summary': summary
                            }
                            
                            # 保存结果 - 传入DataFrame列表
                            saved_files = st.session_state.processor.save_results(
                                output_dir="outputs",
                                separate_files=save_separate, 
                                combined_file=save_combined
                            )
                            
                            print(f"✅ GUI: 推荐文件处理完成")
                            st.success(f"✅ 推荐文件处理完成！生成了 {len(saved_files)} 个输出文件")
                            
                            # 显示结果摘要
                            with st.expander("📊 处理结果摘要", expanded=True):
                                st.write(f"**文件名:** {filename}")
                                st.write(f"**数据行数:** {len(df_processed):,}")
                                st.write(f"**数据列数:** {df_processed.shape[1]}")
                                
                                # 如果是销售数据，显示销售统计
                                if 'Sales' in df_processed.columns:
                                    total_sales = df_processed['Sales'].sum()
                                    avg_sales = df_processed['Sales'].mean()
                                    st.write(f"**总销售额:** {total_sales:,.2f}")
                                    st.write(f"**平均销售额:** {avg_sales:,.2f}")
                                
                                # 显示生成的文件
                                st.write("**生成的文件:**")
                                for file_path in saved_files:
                                    st.write(f"- {file_path}")
                            
                            st.rerun()
                        else:
                            st.error("处理推荐文件时出错")
                            
                    except Exception as e:
                        print(f"❌ GUI: 处理推荐文件时出错: {str(e)}")
                        st.error(f"处理推荐文件时出错: {str(e)}")
        else:
            st.warning(f"⚠️ 未找到推荐文件: {recommended_file}")
            st.info("请使用下方的文件扫描功能选择其他销售数据文件")
    
    with col_quick2:
        # 显示所需字段提示
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem; border: 1px solid #dee2e6;">
            <h5>📋 销售数据必备字段</h5>
            <ul style="font-size: 0.9rem;">
                <li>Order_ID - 订单编号</li>
                <li>Product - 产品名称</li>
                <li>Quantity - 购买数量</li>
                <li>Price - 产品单价</li>
                <li>Order_Date - 订单日期</li>
                <li>Region - 销售地区</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("扫描数据文件")
        
        # 扫描按钮
        col_scan, col_reset = st.columns([1, 1])
        with col_scan:
            if st.button("🔍 扫描文件", type="primary"):
                print(f"\n🔍 GUI: 用户点击扫描文件按钮")
                print(f"扫描路径: {data_path}")
                
                with st.spinner("正在扫描文件..."):
                    try:
                        files = st.session_state.processor.scan_directory(data_path)
                        st.session_state.scanned_files = files
                        st.session_state.scan_completed = True
                        print(f"✅ GUI: 扫描完成，发现 {len(files)} 个文件")
                        st.success(f"发现 {len(files)} 个数据文件")
                        st.rerun()
                        
                    except Exception as e:
                        print(f"❌ GUI: 扫描文件时出错: {str(e)}")
                        st.error(f"扫描文件时出错: {str(e)}")
                        st.session_state.scan_completed = False
        
        with col_reset:
            if st.button("🔄 重新扫描"):
                st.session_state.scanned_files = []
                st.session_state.scan_completed = False
                # 清除之前的选择状态
                keys_to_remove = [key for key in st.session_state.keys() if key.startswith('file_selected_')]
                for key in keys_to_remove:
                    del st.session_state[key]
                st.rerun()
        
        # 显示扫描结果和文件选择
        if st.session_state.scan_completed and st.session_state.scanned_files:
            files = st.session_state.scanned_files
            
            # 限制文件数量提醒
            if len(files) > max_files:
                print(f"⚠️ GUI: 文件数量超过建议限制 ({max_files})，请选择要处理的文件")
                st.warning(f"发现 {len(files)} 个文件，超过建议处理数量 ({max_files})，请选择要处理的文件")
            
            # 显示文件列表并允许选择
            st.subheader("📋 选择要处理的文件")
            
            # 全选/全不选按钮
            col_select1, col_select2, col_select3 = st.columns(3)
            with col_select1:
                if st.button("✅ 全选"):
                    for i, file_path in enumerate(files):
                        st.session_state[f"file_selected_{i}"] = True
                    st.rerun()
            
            with col_select2:
                if st.button("❌ 全不选"):
                    for i, file_path in enumerate(files):
                        st.session_state[f"file_selected_{i}"] = False
                    st.rerun()
            
            with col_select3:
                if st.button("🔄 反选"):
                    for i, file_path in enumerate(files):
                        current_state = st.session_state.get(f"file_selected_{i}", False)
                        st.session_state[f"file_selected_{i}"] = not current_state
                    st.rerun()
            
            # 文件选择列表
            file_data = []
            selected_files = []
            
            # 使用容器来避免重新渲染问题
            file_container = st.container()
            
            with file_container:
                for i, file_path in enumerate(files):
                    file_path_obj = Path(file_path)
                    file_size = file_path_obj.stat().st_size / (1024 * 1024)  # MB
                    
                    # 创建相对路径显示
                    try:
                        relative_path = file_path_obj.relative_to(Path(data_path))
                    except ValueError:
                        relative_path = file_path_obj
                    
                    # 文件选择复选框 - 使用唯一的key
                    checkbox_key = f"file_selected_{i}"
                    is_selected = st.checkbox(
                        f"{relative_path} ({file_size:.2f} MB)",
                        key=checkbox_key,
                        value=st.session_state.get(checkbox_key, True)  # 默认选中
                    )
                    
                    if is_selected:
                        selected_files.append(file_path)
                    
                    file_data.append({
                        "选中": "✅" if is_selected else "❌",
                        "文件名": file_path_obj.name,
                        "相对路径": str(relative_path),
                        "类型": file_path_obj.suffix,
                        "大小 (MB)": f"{file_size:.2f}",
                        "完整路径": str(file_path_obj)
                    })
            
            # 显示文件信息表格
            if file_data:
                st.subheader("📊 文件详情")
                df_files = pd.DataFrame(file_data)
                st.dataframe(df_files, use_container_width=True)
            
            # 显示选中的文件统计
            st.info(f"已选中 {len(selected_files)} / {len(files)} 个文件")
            
            # 处理文件按钮
            if selected_files:
                if st.button("🚀 开始处理选中的文件", type="secondary"):
                    print(f"\n🚀 GUI: 用户点击开始处理文件按钮")
                    print(f"选中的文件数量: {len(selected_files)}")
                    print(f"即将处理的文件:")
                    for i, file_path in enumerate(selected_files, 1):
                        try:
                            relative_path = Path(file_path).relative_to(Path(data_path))
                        except ValueError:
                            relative_path = Path(file_path)
                        print(f"  {i}. {relative_path} ({Path(file_path).stat().st_size / (1024 * 1024):.2f} MB)")
                    process_files(selected_files, save_separate, save_combined)
            else:
                st.warning("请至少选择一个文件进行处理")
        
        elif st.session_state.scan_completed and not st.session_state.scanned_files:
            st.warning(f"在路径 '{data_path}' 中未发现任何 CSV 或 XLSX 文件")
        
        elif not st.session_state.scan_completed:
            st.info("点击 '🔍 扫描文件' 按钮开始扫描数据文件")
    
    with col2:
        st.subheader("📊 处理状态")
        
        if st.session_state.processed_results:
            # 修复数据结构检查
            success_count = 0
            total_count = len(st.session_state.processed_results)
            
            for result in st.session_state.processed_results.values():
                # 检查不同的数据结构
                if isinstance(result, dict) and result.get('success', False):
                    success_count += 1
                elif isinstance(result, tuple) and len(result) == 2:
                    # 如果是元组，说明处理成功
                    success_count += 1
            
            st.metric("成功处理", success_count, delta=f"{total_count} 总计")
            
            # 显示处理结果
            for file_name, result in st.session_state.processed_results.items():
                if isinstance(result, dict):
                    if result.get('success', False):
                        st.success(f"✅ {Path(file_name).name}")
                    else:
                        st.error(f"❌ {Path(file_name).name}: {result.get('error', '未知错误')}")
                elif isinstance(result, tuple) and len(result) == 2:
                    # 元组表示成功处理
                    st.success(f"✅ {Path(file_name).name}")
                else:
                    st.error(f"❌ {Path(file_name).name}: 数据格式错误")
        else:
            st.info("尚未处理任何文件")

def process_files(files, save_separate, save_combined):
    """处理文件"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 控制台输出处理开始信息
    print(f"\n🚀 GUI: 开始处理 {len(files)} 个文件")
    print(f"保存设置: 单独文件={save_separate}, 合并文件={save_combined}")
    for i, file_path in enumerate(files, 1):
        print(f"  {i}. {Path(file_path).name}")
    
    def progress_callback(current, total, message):
        progress = current / total
        progress_bar.progress(progress)
        status_text.text(f"进度: {current}/{total} - {message}")
        # 控制台同步显示进度
        print(f"📊 GUI进度: [{current}/{total}] {message}")
        # 强制刷新页面状态
        time.sleep(0.1)
    
    try:
        # 添加调试信息
        st.info(f"开始处理 {len(files)} 个文件...")
        print(f"💻 GUI: 调用MultiFileProcessor.process_multiple_files()")
        
        # 处理文件
        results = st.session_state.processor.process_multiple_files(files, progress_callback)
        st.session_state.processed_results = results
        
        # 检查处理结果
        success_count = sum(1 for r in results.values() if r.get('success', False))
        print(f"✅ GUI: 文件处理完成 - 成功: {success_count}/{len(files)}")
        st.info(f"文件处理完成：{success_count}/{len(files)} 个文件成功处理")
        
        # 合并数据
        if save_combined:
            print(f"🔗 GUI: 开始合并数据...")
            status_text.text("正在合并数据...")
            st.session_state.combined_data = st.session_state.processor.combine_all_data()
            print(f"✅ GUI: 数据合并完成，合并后数据行数: {len(st.session_state.combined_data)}")
            st.info("数据合并完成")
        
        # 保存结果
        print(f"💾 GUI: 开始保存结果...")
        status_text.text("正在保存结果...")
        saved_files = st.session_state.processor.save_results(
            output_dir="outputs",
            separate_files=save_separate,
            combined_file=save_combined
        )
        
        print(f"✅ GUI: 结果保存完成，保存了 {len(saved_files)} 个文件:")
        
        # 处理返回值 - save_results返回的是列表
        if isinstance(saved_files, list):
            for i, file_path in enumerate(saved_files, 1):
                print(f"  - 文件{i}: {file_path}")
        elif isinstance(saved_files, dict):
            for key, file_path in saved_files.items():
                print(f"  - {key}: {file_path}")
        
        # 显示完成消息
        progress_bar.progress(1.0)
        status_text.text("所有操作完成！")
        
        st.success("🎉 文件处理完成！")
        
        # 显示保存的文件
        st.subheader("💾 已保存文件")
        if isinstance(saved_files, list):
            for i, file_path in enumerate(saved_files, 1):
                st.info(f"📄 文件{i}: {file_path}")
        elif isinstance(saved_files, dict):
            for key, file_path in saved_files.items():
                st.info(f"📄 {key}: {file_path}")
        
        # 显示处理详情
        if results:
            st.subheader("📋 处理详情")
            for filename, result in results.items():
                if result.get('success', False):
                    summary = result.get('summary', {})
                    rows = summary.get('total_rows', 0)
                    st.success(f"✅ {filename}: {rows} 行数据")
                else:
                    error = result.get('error', '未知错误')
                    st.error(f"❌ {filename}: {error}")
        
        print(f"🎯 GUI: 所有处理操作完成!")
        
    except Exception as e:
        progress_bar.progress(0)
        status_text.text("处理失败")
        print(f"❌ GUI: 处理过程中发生错误: {str(e)}")
        st.error(f"处理文件时出错: {str(e)}")
        
        # 添加更详细的错误信息
        import traceback
        error_details = traceback.format_exc()
        print(f"详细错误信息:\n{error_details}")
        st.expander("详细错误信息").code(error_details)

def data_overview_tab():
    """数据概览标签页"""
    st.header("📊 数据概览")
    
    if not st.session_state.processed_results:
        st.info("请先在 '文件处理' 标签页中处理数据文件")
        return
    
    # 总体统计
    col1, col2, col3, col4 = st.columns(4)
    
    total_files = len(st.session_state.processed_results)
    success_files = sum(1 for r in st.session_state.processed_results.values() if r.get('success', False))
    total_records = 0
    total_sales = 0
    
    for result in st.session_state.processed_results.values():
        if result.get('success', False) and 'summary' in result:
            summary = result['summary']
            total_records += summary.get('total_rows', 0)
            total_sales += summary.get('total_sales', 0)
    
    with col1:
        st.metric("处理文件数", success_files, delta=f"{total_files} 总计")
    
    with col2:
        st.metric("总记录数", f"{total_records:,}")
    
    with col3:
        if total_sales > 0:
            st.metric("总销售额", f"{total_sales:,.2f}")
        else:
            st.metric("总销售额", "N/A")
    
    with col4:
        if total_records > 0:
            avg_order = total_sales / total_records
            st.metric("平均订单金额", f"{avg_order:.2f}")
        else:
            st.metric("平均订单金额", "N/A")
    
    # 文件详细信息
    st.subheader("📋 文件详细信息")
    
    file_details = []
    for file_name, result in st.session_state.processed_results.items():
        if result.get('success', False) and 'summary' in result:
            summary = result['summary']
            file_details.append({
                "文件名": file_name,
                "记录数": summary.get('total_rows', 0),
                "列数": summary.get('total_columns', 0),
                "销售额": summary.get('total_sales', 0),
                "状态": "✅ 成功"
            })
        else:
            file_details.append({
                "文件名": file_name,
                "记录数": 0,
                "列数": 0,
                "销售额": 0,
                "状态": f"❌ 失败: {result.get('error', '未知错误')}"
            })
    
    if file_details:
        df_details = pd.DataFrame(file_details)
        st.dataframe(df_details, use_container_width=True)
    
    # 数据预览
    if st.session_state.combined_data is not None:
        st.subheader("🔍 合并数据预览")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.dataframe(st.session_state.combined_data.head(100), use_container_width=True)
        
        with col2:
            st.subheader("📈 快速统计")
            df = st.session_state.combined_data
            
            if 'Sales' in df.columns:
                st.metric("销售额总计", f"{df['Sales'].sum():,.2f}")
                st.metric("最高单笔销售", f"{df['Sales'].max():,.2f}")
                st.metric("最低单笔销售", f"{df['Sales'].min():,.2f}")
            
            if 'Region' in df.columns:
                st.metric("地区数量", df['Region'].nunique())
            
            if 'Product' in df.columns:
                st.metric("产品种类", df['Product'].nunique())

def visualization_tab(chart_theme, show_data_labels):
    """可视化分析标签页"""
    st.header("📈 可视化分析")
    
    if st.session_state.combined_data is None:
        st.info("请先在 '文件处理' 标签页中处理并合并数据")
        return
    
    df = st.session_state.combined_data
    
    # 图表选择
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.subheader("🎨 图表配置")
        chart_type = st.selectbox(
            "选择图表类型",
            ["地区销售分析", "产品销售排行", "销售趋势分析", "销售分布图", "综合仪表板"]
        )
        
        # 数据过滤选项
        if 'Region' in df.columns:
            regions = ['全部'] + list(df['Region'].unique())
            selected_region = st.selectbox("筛选地区", regions)
            if selected_region != '全部':
                df = df[df['Region'] == selected_region]
        
        if 'Source_File' in df.columns:
            files = ['全部'] + list(df['Source_File'].unique())
            selected_file = st.selectbox("筛选文件", files)
            if selected_file != '全部':
                df = df[df['Source_File'] == selected_file]
    
    with col1:
        if chart_type == "地区销售分析":
            create_region_sales_chart(df, chart_theme, show_data_labels)
        
        elif chart_type == "产品销售排行":
            create_product_sales_chart(df, chart_theme, show_data_labels)
        
        elif chart_type == "销售趋势分析":
            create_sales_trend_chart(df, chart_theme, show_data_labels)
        
        elif chart_type == "销售分布图":
            create_sales_distribution_chart(df, chart_theme)
        
        elif chart_type == "综合仪表板":
            create_comprehensive_dashboard(df, chart_theme)

def create_region_sales_chart(df, theme, show_labels):
    """创建地区销售分析图表"""
    if 'Region' not in df.columns or 'Sales' not in df.columns:
        st.warning("数据中缺少 Region 或 Sales 列")
        return
    
    # 按地区聚合销售数据
    region_sales = df.groupby('Region')['Sales'].agg(['sum', 'count', 'mean']).round(2)
    region_sales.columns = ['总销售额 (Total Sales)', '订单数 (Order Count)', '平均订单金额 (Avg Order Value)']
    
    # 创建子图
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('各地区总销售额 (Total Sales by Region)', 
                       '各地区订单数量 (Order Count by Region)', 
                       '各地区平均订单金额 (Avg Order Value by Region)', 
                       '销售额 vs 订单数 (Sales vs Orders)'),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "scatter"}]]
    )
    
    # 总销售额柱状图
    fig.add_trace(
        go.Bar(x=region_sales.index, y=region_sales['总销售额 (Total Sales)'], 
               name='总销售额', showlegend=False,
               text=region_sales['总销售额 (Total Sales)'] if show_labels else None,
               textposition='auto'),
        row=1, col=1
    )
    
    # 订单数量柱状图
    fig.add_trace(
        go.Bar(x=region_sales.index, y=region_sales['订单数 (Order Count)'], 
               name='订单数', showlegend=False,
               text=region_sales['订单数 (Order Count)'] if show_labels else None,
               textposition='auto'),
        row=1, col=2
    )
    
    # 平均订单金额柱状图
    fig.add_trace(
        go.Bar(x=region_sales.index, y=region_sales['平均订单金额 (Avg Order Value)'], 
               name='平均订单金额', showlegend=False,
               text=region_sales['平均订单金额 (Avg Order Value)'] if show_labels else None,
               textposition='auto'),
        row=2, col=1
    )
    
    # 散点图：销售额 vs 订单数
    fig.add_trace(
        go.Scatter(x=region_sales['订单数 (Order Count)'], y=region_sales['总销售额 (Total Sales)'],
                   mode='markers+text', text=region_sales.index,
                   textposition='top center', name='地区',
                   marker=dict(size=10, opacity=0.7)),
        row=2, col=2
    )

    # 配置字体和布局
    fig.update_layout(
        height=600,
        template=theme,
        title_text="地区销售分析 (Regional Sales Analysis)",
        title_x=0.5,
        font=dict(
            family="Microsoft YaHei, SimHei, Arial, sans-serif",
            size=12
        )
    )
    
    # 更新坐标轴字体
    fig.update_xaxes(title_font=dict(family="Microsoft YaHei, SimHei, Arial, sans-serif"))
    fig.update_yaxes(title_font=dict(family="Microsoft YaHei, SimHei, Arial, sans-serif"))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 显示数据表
    st.subheader("📊 地区销售数据 (Regional Sales Data)")
    st.dataframe(region_sales, use_container_width=True)

def create_product_sales_chart(df, theme, show_labels):
    """创建产品销售分析图表"""
    if 'Product' not in df.columns or 'Sales' not in df.columns:
        st.warning("数据中缺少 Product 或 Sales 列")
        return
    
    # 按产品聚合销售数据
    product_sales = df.groupby('Product')['Sales'].agg(['sum', 'count', 'mean']).round(2)
    product_sales.columns = ['总销售额 (Total Sales)', '订单数 (Order Count)', '平均订单金额 (Avg Order Value)']
    product_sales = product_sales.sort_values('总销售额 (Total Sales)', ascending=False)
    
    # 创建子图
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('产品总销售额排名 (Product Sales Ranking)', 
                       '产品订单数量 (Product Order Count)', 
                       '产品平均订单金额 (Product Avg Order Value)', 
                       '销售额分布 (Sales Distribution)'),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "histogram"}]]
    )
    
    # 总销售额柱状图（前10名）
    top_10 = product_sales.head(10)
    fig.add_trace(
        go.Bar(x=top_10.index, y=top_10['总销售额 (Total Sales)'], 
               name='总销售额', showlegend=False,
               text=top_10['总销售额 (Total Sales)'] if show_labels else None,
               textposition='auto'),
        row=1, col=1
    )
    
    # 订单数量柱状图（前10名）
    fig.add_trace(
        go.Bar(x=top_10.index, y=top_10['订单数 (Order Count)'], 
               name='订单数', showlegend=False,
               text=top_10['订单数 (Order Count)'] if show_labels else None,
               textposition='auto'),
        row=1, col=2
    )
    
    # 平均订单金额柱状图（前10名）
    fig.add_trace(
        go.Bar(x=top_10.index, y=top_10['平均订单金额 (Avg Order Value)'], 
               name='平均订单金额', showlegend=False,
               text=top_10['平均订单金额 (Avg Order Value)'] if show_labels else None,
               textposition='auto'),
        row=2, col=1
    )
    
    # 销售额分布直方图
    fig.add_trace(
        go.Histogram(x=df['Sales'], nbinsx=30, name='销售额分布', showlegend=False),
        row=2, col=2
    )

    # 配置字体和布局
    fig.update_layout(
        height=600,
        template=theme,
        title_text="产品销售分析 (Product Sales Analysis)",
        title_x=0.5,
        font=dict(
            family="Microsoft YaHei, SimHei, Arial, sans-serif",
            size=12
        )
    )
    
    # 更新坐标轴字体
    fig.update_xaxes(title_font=dict(family="Microsoft YaHei, SimHei, Arial, sans-serif"))
    fig.update_yaxes(title_font=dict(family="Microsoft YaHei, SimHei, Arial, sans-serif"))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 显示数据表
    st.subheader("📊 产品销售数据 (Product Sales Data)")
    st.dataframe(product_sales.head(20), use_container_width=True)

def create_sales_trend_chart(df, theme, show_labels):
    """创建销售趋势分析图表"""
    if 'Date' not in df.columns or 'Sales' not in df.columns:
        st.warning("数据中缺少 Date 或 Sales 列")
        return
    
    # 确保Date列是datetime类型
    df['Date'] = pd.to_datetime(df['Date'])
    
    # 按日期聚合销售数据
    daily_sales = df.groupby('Date')['Sales'].agg(['sum', 'count', 'mean']).round(2)
    daily_sales.columns = ['日销售额 (Daily Sales)', '订单数 (Order Count)', '平均订单金额 (Avg Order Value)']
    
    # 创建子图
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('日销售额趋势 (Daily Sales Trend)', 
                       '订单数量趋势 (Order Count Trend)', 
                       '平均订单金额趋势 (Avg Order Value Trend)', 
                       '销售额分布 (Sales Distribution)'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"type": "histogram"}]]
    )
    
    # 日销售额趋势线
    fig.add_trace(
        go.Scatter(x=daily_sales.index, y=daily_sales['日销售额 (Daily Sales)'],
                   mode='lines+markers', name='日销售额',
                   line=dict(width=2)),
        row=1, col=1
    )
    
    # 订单数量趋势线
    fig.add_trace(
        go.Scatter(x=daily_sales.index, y=daily_sales['订单数 (Order Count)'],
                   mode='lines+markers', name='订单数',
                   line=dict(width=2)),
        row=1, col=2
    )
    
    # 平均订单金额趋势线
    fig.add_trace(
        go.Scatter(x=daily_sales.index, y=daily_sales['平均订单金额 (Avg Order Value)'],
                   mode='lines+markers', name='平均订单金额',
                   line=dict(width=2)),
        row=2, col=1
    )
    
    # 销售额分布直方图
    fig.add_trace(
        go.Histogram(x=df['Sales'], nbinsx=30, name='销售额分布', showlegend=False),
        row=2, col=2
    )

    # 配置字体和布局
    fig.update_layout(
        height=600,
        template=theme,
        title_text="销售趋势分析 (Sales Trend Analysis)",
        title_x=0.5,
        font=dict(
            family="Microsoft YaHei, SimHei, Arial, sans-serif",
            size=12
        ),
        showlegend=False
    )
    
    # 更新坐标轴字体
    fig.update_xaxes(title_font=dict(family="Microsoft YaHei, SimHei, Arial, sans-serif"))
    fig.update_yaxes(title_font=dict(family="Microsoft YaHei, SimHei, Arial, sans-serif"))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 显示数据表
    st.subheader("📊 销售趋势数据 (Sales Trend Data)")
    st.dataframe(daily_sales.tail(10), use_container_width=True)

def create_sales_distribution_chart(df, theme):
    """创建销售分布分析图表"""
    if 'Sales' not in df.columns:
        st.warning("数据中缺少 Sales 列")
        return
    
    # 创建子图
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('销售额直方图 (Sales Histogram)', 
                       '销售额箱线图 (Sales Box Plot)', 
                       '销售额密度图 (Sales Density)', 
                       '销售额累积分布 (Sales CDF)'),
        specs=[[{"type": "histogram"}, {"type": "box"}],
               [{"type": "scatter"}, {"type": "scatter"}]]
    )
    
    # 销售额直方图
    fig.add_trace(
        go.Histogram(x=df['Sales'], nbinsx=30, name='销售额分布', showlegend=False),
        row=1, col=1
    )
    
    # 销售额箱线图
    fig.add_trace(
        go.Box(y=df['Sales'], name='销售额', showlegend=False),
        row=1, col=2
    )
    
    # 销售额密度图（近似）
    from scipy import stats
    import numpy as np
    
    # 计算核密度估计
    density = stats.gaussian_kde(df['Sales'].dropna())
    x_range = np.linspace(df['Sales'].min(), df['Sales'].max(), 100)
    y_density = density(x_range)
    
    fig.add_trace(
        go.Scatter(x=x_range, y=y_density, mode='lines', 
                   name='密度', fill='tonexty', showlegend=False),
        row=2, col=1
    )
    
    # 销售额累积分布
    sorted_sales = np.sort(df['Sales'].dropna())
    y_cdf = np.arange(1, len(sorted_sales) + 1) / len(sorted_sales)
    
    fig.add_trace(
        go.Scatter(x=sorted_sales, y=y_cdf, mode='lines', 
                   name='累积分布', showlegend=False),
        row=2, col=2
    )

    # 配置字体和布局
    fig.update_layout(
        height=600,
        template=theme,
        title_text="销售分布分析 (Sales Distribution Analysis)",
        title_x=0.5,
        font=dict(
            family="Microsoft YaHei, SimHei, Arial, sans-serif",
            size=12
        )
    )
    
    # 更新坐标轴字体
    fig.update_xaxes(title_font=dict(family="Microsoft YaHei, SimHei, Arial, sans-serif"))
    fig.update_yaxes(title_font=dict(family="Microsoft YaHei, SimHei, Arial, sans-serif"))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 显示统计信息
    st.subheader("📊 销售统计信息 (Sales Statistics)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("平均值 (Mean)", f"{df['Sales'].mean():.2f}")
    with col2:
        st.metric("中位数 (Median)", f"{df['Sales'].median():.2f}")
    with col3:
        st.metric("标准差 (Std Dev)", f"{df['Sales'].std():.2f}")
    with col4:
        st.metric("变异系数 (CV)", f"{df['Sales'].std()/df['Sales'].mean():.2f}")
    
    # 分位数信息
    st.subheader("📈 分位数信息 (Quantile Information)")
    quantiles = df['Sales'].quantile([0.25, 0.5, 0.75, 0.9, 0.95]).round(2)
    quantile_df = pd.DataFrame({
        '分位数 (Quantile)': ['25%', '50% (中位数)', '75%', '90%', '95%'],
        '销售额 (Sales Amount)': quantiles.values
    })
    st.dataframe(quantile_df, use_container_width=True)

def create_comprehensive_dashboard(df, theme):
    """创建综合仪表板"""
    st.subheader("🎯 综合仪表板")
    
    # 关键指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sales = df['Sales'].sum() if 'Sales' in df.columns else 0
        st.metric("总销售额", f"{total_sales:,.2f}")
    
    with col2:
        total_orders = len(df)
        st.metric("总订单数", f"{total_orders:,}")
    
    with col3:
        avg_order = total_sales / total_orders if total_orders > 0 else 0
        st.metric("平均订单金额", f"{avg_order:.2f}")
    
    with col4:
        unique_products = df['Product'].nunique() if 'Product' in df.columns else 0
        st.metric("产品种类", unique_products)
    
    # 创建多维度分析图
    if all(col in df.columns for col in ['Region', 'Product', 'Sales']):
        
        # 热力图：地区 vs 产品
        pivot_table = df.pivot_table(
            values='Sales', 
            index='Region', 
            columns='Product', 
            aggfunc='sum', 
            fill_value=0
        )
        
        # 只显示销售额最高的前10个产品
        top_products = df.groupby('Product')['Sales'].sum().nlargest(10).index
        pivot_table = pivot_table[top_products]
        
        fig_heatmap = px.imshow(
            pivot_table,
            labels=dict(x="产品", y="地区", color="销售额"),
            title="地区-产品销售热力图",
            template=theme
        )
        
        # 更新热力图字体
        fig_heatmap.update_layout(
            font=dict(
                family="Microsoft YaHei, SimHei, Arial, sans-serif",
                size=12
            )
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # 气泡图：销售额 vs 订单数 (按地区)
        if 'Region' in df.columns:
            bubble_data = df.groupby('Region').agg({
                'Sales': ['sum', 'count', 'mean']
            }).round(2)
            bubble_data.columns = ['总销售额', '订单数', '平均订单金额']
            bubble_data = bubble_data.reset_index()
            
            fig_bubble = px.scatter(
                bubble_data,
                x='订单数',
                y='总销售额',
                size='平均订单金额',
                color='Region',
                hover_name='Region',
                title="地区销售气泡图 (气泡大小=平均订单金额)",
                template=theme
            )
            
            # 更新气泡图字体
            fig_bubble.update_layout(
                font=dict(
                    family="Microsoft YaHei, SimHei, Arial, sans-serif",
                    size=12
                )
            )
            
            st.plotly_chart(fig_bubble, use_container_width=True)

def report_export_tab():
    """报告导出标签页"""
    st.header("📋 报告导出")
    
    if st.session_state.combined_data is None:
        st.info("请先处理数据文件")
        return
    
    # 生成报告
    if st.button("📄 生成分析报告", type="primary"):
        try:
            report = st.session_state.processor.generate_combined_report()
            
            # 显示报告内容
            st.subheader("📊 分析报告")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📈 总体统计")
                st.write(f"**处理文件数:** {report['total_files_processed']}")
                st.write(f"**总记录数:** {report['total_records']:,}")
                
                if report['total_sales'] > 0:
                    st.write(f"**总销售额:** {report['total_sales']:,.2f}")
                    st.write(f"**平均订单金额:** {report['avg_order_value']:,.2f}")
                
                if report['date_range']:
                    st.write(f"**数据时间范围:** {report['date_range']['start']} 至 {report['date_range']['end']}")
            
            with col2:
                st.markdown("### 🏆 排行榜")
                
                if report['top_regions']:
                    st.markdown("**销售额最高的地区:**")
                    for i, (region, sales) in enumerate(list(report['top_regions'].items())[:5], 1):
                        st.write(f"{i}. {region}: {sales:,.2f}")
                
                if report['top_products']:
                    st.markdown("**销售额最高的产品:**")
                    for i, (product, sales) in enumerate(list(report['top_products'].items())[:5], 1):
                        st.write(f"{i}. {product}: {sales:,.2f}")
            
            # 文件分解统计
            if report['file_breakdown']:
                st.subheader("📁 文件分解统计")
                file_breakdown_df = pd.DataFrame(report['file_breakdown']).T
                st.dataframe(file_breakdown_df, use_container_width=True)
            
            # 导出选项
            st.subheader("💾 导出选项")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 导出数据 (CSV)"):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"sales_analysis_data_{timestamp}.csv"
                    st.session_state.combined_data.to_csv(filename, index=False, encoding='utf-8-sig')
                    st.success(f"数据已导出到: {filename}")
            
            with col2:
                if st.button("📋 导出报告 (TXT)"):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"sales_analysis_report_{timestamp}.txt"
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write("销售数据分析报告\n")
                        f.write("=" * 50 + "\n\n")
                        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"处理文件数: {report['total_files_processed']}\n")
                        f.write(f"总记录数: {report['total_records']}\n")
                        
                        if report['total_sales'] > 0:
                            f.write(f"总销售额: {report['total_sales']:,.2f}\n")
                            f.write(f"平均订单金额: {report['avg_order_value']:,.2f}\n")
                        
                        f.write("\n地区销售排行:\n")
                        for region, sales in report['top_regions'].items():
                            f.write(f"- {region}: {sales:,.2f}\n")
                        
                        f.write("\n产品销售排行:\n")
                        for product, sales in report['top_products'].items():
                            f.write(f"- {product}: {sales:,.2f}\n")
                    
                    st.success(f"报告已导出到: {filename}")
            
            with col3:
                if st.button("📈 导出图表数据"):
                    # 这里可以添加图表数据的导出功能
                    st.info("图表数据导出功能开发中...")
            
        except Exception as e:
            st.error(f"生成报告时出错: {str(e)}")

if __name__ == "__main__":
    main() 