# 销售数据分析项目

## 项目概述

本项目是一个完整的销售数据分析解决方案，旨在通过数据科学方法分析销售数据，提供业务洞察和决策支持。项目包含数据清洗、探索性分析、可视化和报告生成等完整流程。

## 项目结构

```
Sales-Analysis-Project/
│
├── venv/                        # 虚拟环境 Virtual environment
│   └── ...                      # Python虚拟环境文件 Python virtual environment files
│ 
├── data/                        # 数据存储区 Data storage area
│   ├── raw_sales_data.csv       # 原始销售数据 Raw sales data (39KB)
│   ├── converted_online_retail_II.csv  # 转换后的在线零售数据 Converted online retail data (79MB)
│   ├── small_dataset.csv        # 小型测试数据集 Small test dataset (502行)
│   ├── medium_dataset.csv       # 中等规模数据集 Medium-sized dataset (2002行)
│   ├── large_dataset.csv        # 大型数据集 Large dataset (10002行)
│   ├── product_category_dataset.csv    # 产品分类数据集 Product category dataset (2502行)
│   ├── regional_focus_dataset.csv      # 区域专注数据集 Regional focus dataset (1502行)
│   ├── seasonal_dataset.csv     # 季节性数据集 Seasonal dataset (3002行)
│   └── high_missing_dataset.csv # 高缺失值数据集 Dataset with high missing values (1002行)
│
├── notebooks/                   # Jupyter Notebook 脚本区 Jupyter Notebook script area
│   ├── 01_data_loading.ipynb    # 数据加载脚本 Data loading script
│   ├── 02_data_cleaning.ipynb   # 数据清洗脚本 Data cleaning script
│   ├── 03_outlier_handling.ipynb # 异常值处理脚本 Outlier handling script
│   ├── 04_eda_visualization.ipynb # 探索性数据分析与可视化 Exploratory data analysis & visualization
│   └── 05_summary_report.ipynb  # 汇总报告脚本 Summary report script
│
├── outputs/                     # 输出结果区（图像和表格） Output result area (images and tables)
│   ├── eg/                      # 示例输出子目录 Example output subdirectory
│   ├── cleaned_data.csv         # 清洗后的数据 Cleaned data (待生成 To be generated)
│   ├── sales_by_region.png      # 区域销售图表 Sales by region chart (待生成 To be generated)
│   ├── summary_stats.csv        # 汇总统计表 Summary statistics table (待生成 To be generated)
│   └── analysis_report.md       # Markdown 分析报告 Analysis report in Markdown (待生成 To be generated)
│
├── scripts/                     # 可复用脚本函数库 Reusable script function library 
│   ├── __pycache__/             # Python 缓存目录 Python cache directory
│   ├── data_utils.py            # 数据工具函数库 Data utility functions library (197行)
│   │                            # 功能：封装数据清洗、异常处理、统计分析等函数
│   │                            # Functions: Data cleaning, exception handling, statistical analysis
│   └── multi_file_processor.py  # 多文件批量处理器 Multi-file batch processor (1116行)
│                                # 功能：批量处理多个数据文件，支持并行处理
│                                # Functions: Batch processing multiple data files with parallel support
│
├── report/                      # 项目报告目录 Project report directory
│
├── README.md                    # 项目说明文件 Project description document (251行)
├── requirements.txt             # Python依赖包列表 Python dependencies list (57行)
│
├── main_analysis.py             # 主分析脚本 Main analysis script (348行)
│                                # 功能：核心数据分析逻辑，整合各模块功能
│                                # Functions: Core data analysis logic, integrating all modules
│
├── data_processor.py            # 数据处理器 Data processor (276行)
│                                # 功能：专门处理数据预处理和转换任务
│                                # Functions: Specialized data preprocessing and transformation
│
├── sales_analysis_gui.py        # 图形用户界面主程序 GUI main program (1195行)
│                                # 功能：提供交互式销售数据分析界面
│                                # Functions: Interactive sales data analysis interface
│
├── start_gui.py                 # GUI启动脚本 GUI startup script (109行)
│                                # 功能：简化GUI程序启动流程
│                                # Functions: Simplify GUI program startup process
│
├── start_gui.bat                # Windows一键启动脚本 Windows one-click startup script (200行)
│                                # 功能：Windows批处理文件，一键启动GUI应用
│                                # Functions: Windows batch file for one-click GUI startup
│
└── check_file.py                # 文件检查工具 File checking utility (32行)
                                 # 功能：检查项目文件完整性和数据格式
                                 # Functions: Check project file integrity and data formats
```

## 功能特性

- **数据清洗**: 自动处理缺失值、重复数据和数据类型转换
- **异常值检测**: 使用统计方法识别和处理异常值
- **探索性分析**: 全面的数据探索和统计分析
- **可视化**: 生成多种类型的图表和可视化
- **报告生成**: 自动生成详细的分析报告
- **模块化设计**: 可重用的数据处理函数

## 数据流程图（Data Flow Diagram）
原始数据 Raw Data → 数据加载 Data Loading → 数据清洗 Data Cleaning → 
异常值处理 Outlier Handling → 探索性分析 EDA → 数据可视化 Visualization → 
报告生成 Report Generation → 结果输出 Result Output

## 技术栈与工具（Technology Stack & Tools）
```
┌─────────────────┬──────────────────────┬─────────────────────────────┐
│ 分类 Category   │ 工具/技术 Tools/Tech  │ 用途 Purpose                │
├─────────────────┼──────────────────────┼─────────────────────────────┤
│ 数据处理        │ pandas, numpy        │ 数据清洗、计算、分析          │
│ Data Processing │                      │ Data cleaning, computation  │
├─────────────────┼──────────────────────┼─────────────────────────────┤
│ 数据可视化      │ matplotlib, seaborn, │ 图表生成、统计可视化          │
│ Visualization   │ plotly               │ Chart generation, stats viz │
├─────────────────┼──────────────────────┼─────────────────────────────┤
│ 开发环境        │ Jupyter Notebook,    │ 脚本编写与交互式开发          │
│ Development     │ VSCode, Python       │ Script writing & interactive│
├─────────────────┼──────────────────────┼─────────────────────────────┤
│ 用户界面        │ tkinter, GUI工具包   │ 图形界面开发                  │
│ User Interface  │ GUI toolkit          │ Graphical interface dev     │
├─────────────────┼──────────────────────┼─────────────────────────────┤
│ 报告输出        │ Markdown, CSV        │ 结果报告和数据导出            │
│ Report Output   │                      │ Result reporting & export   │
└─────────────────┴──────────────────────┴─────────────────────────────┘
```

## 安装要求

### Python版本
- Python 3.10 或更高版本

### 依赖包
```
pandas>=1.3.0
numpy>=1.21.0
matplotlib>=3.4.0
seaborn>=0.11.0
jupyter>=1.0.0
scikit-learn>=1.0.0
```

## 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd Sales-Data-Analysis
```

2. **创建虚拟环境（推荐）**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **安装依赖包**
```bash
pip install -r requirements.txt
```

## 使用方法

### 方法1: 运行主脚本（推荐）

执行完整的数据分析流程：

```bash
python main_analysis.py
```

这将自动执行以下步骤：
1. 数据加载与检查
2. 数据清洗
3. 异常值处理
4. 探索性分析
5. 可视化生成
6. 报告生成

### 方法2: 使用Jupyter笔记本

1. **启动Jupyter**
```bash
jupyter notebook
```

2. **按顺序执行笔记本**
   - `01_data_loading.ipynb` - 数据加载
   - `02_data_cleaning.ipynb` - 数据清洗
   - `03_outlier_handling.ipynb` - 异常值处理
   - `04_eda_visualization.ipynb` - 探索性分析
   - `05_summary_report.ipynb` - 总结报告

### 方法3: 使用脚本函数

```python
from scripts.data_utils import *

# 加载数据
df = load_and_check_data('data/raw_sales_data.csv')

# 清洗数据
df_cleaned = clean_data(df)

# 处理异常值
df_processed = handle_outliers(df_cleaned)

# 探索性分析
df_analyzed, grouped_data = exploratory_analysis(df_processed)

# 保存结果
save_results(df_analyzed, grouped_data, 'outputs')
```

## 数据格式

### 输入数据格式
项目期望的CSV文件应包含以下列：

| 列名 | 数据类型 | 描述 |
|------|----------|------|
| Order_ID | string | 订单ID |
| Order_Date | datetime | 订单日期 |
| Region | string | 销售地区 |
| Product | string | 产品名称 |
| Quantity | int | 购买数量 |
| Price | float | 产品单价 |

### 输出文件
- `cleaned_data.csv`: 清洗后的完整数据集
- `summary_stats.csv`: 按地区分组的统计摘要
- `sales_by_region.png`: 各地区销售额柱状图
- `comprehensive_analysis.png`: 综合分析图表
- `analysis_report.md`: 详细的分析报告

## 分析内容

### 1. 数据质量评估
- 缺失值检查
- 数据类型验证
- 重复数据识别
- 异常值检测

### 2. 描述性统计
- 基本统计指标
- 数据分布分析
- 相关性分析

### 3. 业务分析
- 地区销售表现
- 产品销售排名
- 时间趋势分析
- 客户行为分析

### 4. 可视化
- 销售额分布图
- 地区对比图
- 产品排名图
- 散点图分析

## 自定义配置

### 修改数据源
编辑 `main_analysis.py` 中的数据文件路径：
```python
df = load_and_check_data('your_data_file.csv')
```

### 调整分析参数
在 `scripts/data_utils.py` 中修改分析参数：
```python
# 异常值处理阈值
OUTLIER_THRESHOLD = 3.0

# 数据清洗规则
MIN_QUANTITY = 1
MIN_PRICE = 0.01
```

### 自定义可视化
在 `main_analysis.py` 的 `generate_visualizations` 函数中添加新的图表类型。

## 故障排除

### 常见问题

1. **字体显示问题**
   - 确保系统安装了中文字体
   - 或修改 `plt.rcParams['font.sans-serif']` 设置

2. **依赖包版本冲突**
   - 使用虚拟环境
   - 检查 `requirements.txt` 中的版本要求

3. **数据文件路径错误**
   - 确保数据文件存在于正确路径
   - 检查文件权限

### 调试模式
在脚本中添加调试信息：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 项目Issues: [GitHub Issues](https://github.com/Odelialan/Sales-Data-Analysis.git/issues)
- 邮箱: lanhanyue1996@gmail.com

## 更新日志

### v1.0.0 (2025-06-22)
- 初始版本发布
- 基本数据分析功能
- 可视化图表生成
- 报告自动生成

---

**注意**: 本项目仅供学习和研究使用。在实际业务环境中使用时，请确保数据安全和隐私保护。 
