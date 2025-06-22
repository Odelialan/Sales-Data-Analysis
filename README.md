# 销售数据分析项目

## 项目概述

本项目是一个完整的销售数据分析解决方案，旨在通过数据科学方法分析销售数据，提供业务洞察和决策支持。项目包含数据清洗、探索性分析、可视化和报告生成等完整流程。

## 项目结构

```
Sales-Data-Analysis/
├── data/                   # 数据文件目录
│   └── raw_sales_data.csv  # 原始销售数据
├── notebooks/              # Jupyter笔记本
│   ├── 01_data_loading.ipynb      # 数据加载
│   ├── 02_data_cleaning.ipynb     # 数据清洗
│   ├── 03_outlier_handling.ipynb  # 异常值处理
│   ├── 04_eda_visualization.ipynb # 探索性分析
│   └── 05_summary_report.ipynb    # 总结报告
├── outputs/                # 输出文件目录
│   ├── cleaned_data.csv    # 清洗后的数据
│   ├── summary_stats.csv   # 统计摘要
│   ├── sales_by_region.png # 地区销售图表
│   └── comprehensive_analysis.png # 综合分析图表
├── report/                 # 报告目录
│   └── analysis_report.md  # 分析报告
├── scripts/                # Python脚本
│   └── data_utils.py       # 数据处理工具函数
├── main_analysis.py        # 主执行脚本
├── requirements.txt        # 依赖包列表
└── README.md              # 项目说明文档
```

## 功能特性

- **数据清洗**: 自动处理缺失值、重复数据和数据类型转换
- **异常值检测**: 使用统计方法识别和处理异常值
- **探索性分析**: 全面的数据探索和统计分析
- **可视化**: 生成多种类型的图表和可视化
- **报告生成**: 自动生成详细的分析报告
- **模块化设计**: 可重用的数据处理函数

## 安装要求

### Python版本
- Python 3.7 或更高版本

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
- 项目Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 邮箱: your-email@example.com

## 更新日志

### v1.0.0 (2025-06-22)
- 初始版本发布
- 基本数据分析功能
- 可视化图表生成
- 报告自动生成

---

**注意**: 本项目仅供学习和研究使用。在实际业务环境中使用时，请确保数据安全和隐私保护。 
