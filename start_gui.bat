@echo off
chcp 65001
title 销售数据分析系统 - GUI启动器

echo ============================================================
echo                📊 销售数据分析系统 - GUI启动器
echo ============================================================
echo.

REM 检查Python是否安装
echo 🔍 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.7或更高版本
    echo 💡 建议: 从 https://www.python.org/downloads/ 下载安装Python
    pause
    exit /b 1
)

REM 获取Python版本信息
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python已安装 (版本: %PYTHON_VERSION%)

REM 检查Python版本是否符合要求 (3.7+)
python -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ 警告: Python版本过低，建议使用Python 3.7或更高版本
    echo 当前版本: %PYTHON_VERSION%
    echo 是否继续? (可能会出现兼容性问题)
    set /p continue="继续执行? (y/n): "
    if /i not "%continue%"=="y" (
        echo 👋 已取消执行
        pause
        exit /b 1
    )
)

REM 检查并处理虚拟环境
if exist "venv\" (
    echo 🔄 发现现有虚拟环境，正在激活...
    call venv\Scripts\activate.bat
    if errorlevel 1 (
        echo ❌ 错误: 虚拟环境激活失败
        echo 🔧 尝试重新创建虚拟环境...
        rmdir /s /q venv
        goto CREATE_VENV
    )
    echo ✅ 虚拟环境激活成功
) else (
    :CREATE_VENV
    echo 🆕 首次运行或虚拟环境不存在，正在创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 错误: 虚拟环境创建失败
        echo 💡 可能原因:
        echo    - Python安装不完整
        echo    - 磁盘空间不足
        echo    - 权限不足
        pause
        exit /b 1
    )
    
    echo 🔄 激活新创建的虚拟环境...
    call venv\Scripts\activate.bat
    if errorlevel 1 (
        echo ❌ 错误: 新虚拟环境激活失败
        pause
        exit /b 1
    )
    echo ✅ 虚拟环境创建并激活成功
)

REM 检查pip是否可用
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: pip不可用，尝试修复...
    python -m ensurepip --upgrade >nul 2>&1
    if errorlevel 1 (
        echo ❌ 错误: 无法修复pip
        pause
        exit /b 1
    )
)

REM 检查requirements.txt
if not exist "requirements.txt" (
    echo ❌ 错误: 未找到requirements.txt文件
    echo 💡 请确保在项目根目录中运行此脚本
    pause
    exit /b 1
)

REM 升级pip到最新版本
echo 🔧 升级pip到最新版本...
python -m pip install --upgrade pip >nul 2>&1

REM 安装/更新依赖包
echo 🔧 检查并安装/更新依赖包...
echo 📦 这可能需要几分钟时间，请耐心等待...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 错误: 依赖包安装失败
    echo 💡 可能解决方案:
    echo    - 检查网络连接
    echo    - 尝试使用国内镜像: pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
    echo    - 手动安装关键包: pip install streamlit pandas numpy matplotlib
    set /p retry="是否尝试使用清华镜像重新安装? (y/n): "
    if /i "%retry%"=="y" (
        echo 🔄 使用清华镜像重新安装...
        pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
        if errorlevel 1 (
            echo ❌ 镜像安装也失败，请检查网络或手动安装
            pause
            exit /b 1
        )
    ) else (
        pause
        exit /b 1
    )
)
echo ✅ 依赖包安装/更新完成

REM 创建必要目录
echo 📁 检查项目目录结构...
if not exist "data\" (
    mkdir data
    echo ✅ 创建 data 目录
)
if not exist "outputs\" (
    mkdir outputs
    echo ✅ 创建 outputs 目录
)
if not exist "scripts\" (
    mkdir scripts
    echo ✅ 创建 scripts 目录
)
if not exist "report\" (
    mkdir report
    echo ✅ 创建 report 目录
)
if not exist "notebooks\" (
    mkdir notebooks
    echo ✅ 创建 notebooks 目录
)

echo ✅ 项目目录结构已就绪

REM 检查主要文件是否存在
if not exist "sales_analysis_gui.py" (
    echo ❌ 错误: 未找到主程序文件 sales_analysis_gui.py
    echo 💡 请确保在正确的项目目录中运行此脚本
    pause
    exit /b 1
)

if not exist "start_gui.py" (
    echo ❌ 错误: 未找到启动脚本 start_gui.py
    echo 💡 请确保在正确的项目目录中运行此脚本
    pause
    exit /b 1
)

REM 检查关键Python包是否正确安装
echo 🔍 验证关键组件...
python -c "import streamlit, pandas, numpy, matplotlib, plotly" >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 关键Python包导入失败
    echo 💡 尝试重新安装核心包...
    pip install streamlit pandas numpy matplotlib plotly
    if errorlevel 1 (
        echo ❌ 核心包安装失败，无法启动应用
        pause
        exit /b 1
    )
)

REM 启动GUI应用
echo.
echo 🚀 正在启动销售数据分析GUI...
echo 📊 Web界面将在浏览器中自动打开
echo 🔗 默认地址: http://localhost:8501
echo ⏹️ 按 Ctrl+C 停止应用
echo 💡 如果浏览器未自动打开，请手动访问上述地址
echo.

REM 启动应用并处理可能的错误
python start_gui.py
if errorlevel 1 (
    echo.
    echo ❌ 应用启动时发生错误
    echo 💡 可能的解决方案:
    echo    - 检查端口8501是否被占用
    echo    - 重新运行此脚本
    echo    - 手动运行: streamlit run sales_analysis_gui.py
)

echo.
echo 👋 应用已停止
echo 💡 如需重新启动，请再次运行此脚本
pause 