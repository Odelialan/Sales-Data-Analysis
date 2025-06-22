#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
销售数据分析GUI启动脚本

快速启动Streamlit Web应用
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """检查必要的依赖包"""
    required_packages = [
        'streamlit',
        'pandas',
        'numpy',
        'plotly',
        'scipy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies():
    """安装缺失的依赖包"""
    print("🔧 正在安装缺失的依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖包安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        return False

def start_streamlit_app():
    """启动Streamlit应用"""
    print("🚀 正在启动销售数据分析GUI...")
    print("📊 Web界面将在浏览器中打开")
    print("🔗 默认地址: http://localhost:8501")
    print("⏹️ 按 Ctrl+C 停止应用")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "sales_analysis_gui.py",
            "--server.port=8501",
            "--server.headless=false",
            "--browser.serverAddress=localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("📊 销售数据分析系统 - GUI启动器")
    print("=" * 60)
    
    # 检查当前工作目录
    current_dir = Path.cwd()
    gui_file = current_dir / "sales_analysis_gui.py"
    
    if not gui_file.exists():
        print("❌ 找不到 sales_analysis_gui.py 文件")
        print("请确保在正确的项目目录中运行此脚本")
        return
    
    # 检查依赖包
    print("🔍 检查依赖包...")
    missing = check_dependencies()
    
    if missing:
        print(f"⚠️ 缺失依赖包: {', '.join(missing)}")
        install_choice = input("是否自动安装? (y/n): ").lower().strip()
        
        if install_choice in ['y', 'yes']:
            if not install_dependencies():
                print("❌ 无法自动安装依赖包，请手动运行: pip install -r requirements.txt")
                return
        else:
            print("❌ 请手动安装依赖包后再运行")
            return
    else:
        print("✅ 所有依赖包已安装")
    
    # 创建必要的目录
    os.makedirs("data", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("scripts", exist_ok=True)
    
    print("📁 项目目录结构已就绪")
    
    # 启动应用
    start_streamlit_app()

if __name__ == "__main__":
    main() 