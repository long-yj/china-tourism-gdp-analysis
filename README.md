# China Tourism & GDP Data Visualization Analysis

[中文](#中文说明) | [English](#english-description)

## 中文说明

### 📊 项目简介

这是一个基于Python的中国旅游与GDP数据可视化分析系统，对2009-2023年间的全国及省级旅游数据、GDP数据进行深度分析和可视化展示。项目生成包括时序图、柱状图、散点图、热力图和交互式地图在内的22+张专业图表。

### ✨ 主要功能

- **全国层面时间序列分析**
  - GDP总值变化趋势
  - 人均收入与消费水平对比
  - 国内外旅游收入和游客数量对比

- **省级横向对比分析**
  - 各省GDP排名（最新年份及10年前对比）
  - 各省旅游外汇收入排名
  - 各省接待外国游客数量排名
  - 各省GDP增长率排名

- **关联性分析**
  - GDP与旅游外汇收入关联性散点图
  - GDP与接待外国游客关联性分析
  - 省级GDP与旅游指标相关性热力图

- **地理可视化**
  - 各省GDP分布地图（交互式HTML）
  - 各省旅游外汇收入分布地图
  - 各省接待外国游客分布地图

- **特色分析**
  - 海南省月度旅游数据趋势分析

### 🛠️ 技术栈

- **Python 3.7+**
- **数据处理**: Pandas, NumPy
- **数据可视化**: Matplotlib, Seaborn
- **地理可视化**: Pyecharts
- **数据源**: Excel格式的年度统计数据

### 📁 项目结构

```
china-tourism-gdp-analysis/
├── data/                          # 数据文件夹
│   ├── 全国居民人均收入情况年度数据.xlsx
│   ├── 国内旅游情况年度数据.xlsx
│   ├── 国内生成总值年度数据.xlsx
│   ├── 地区生产总值分省年度数据.xlsx
│   ├── 国际旅游外汇收入分省年度数据.xlsx
│   ├── 接待外国人游客分省年度数据.xlsx
│   ├── 旅游业发展情况年度数据.xlsx
│   └── 海南旅游统计数据.xlsx
├── output_charts/                 # 输出图表文件夹
│   ├── *.png                     # 静态图表
│   └── *.html                    # 交互式地图
├── data_analysis.py              # 主分析脚本
├── ks.py                         # 辅助脚本1
├── ks2.py                        # 辅助脚本2
├── 提取数据.py                   # 数据提取工具
├── 数据加载.py                   # 数据加载工具
└── 数据提取2.py                  # 数据提取工具2
```

### 🚀 快速开始

#### 1. 环境要求

```bash
pip install pandas matplotlib seaborn pyecharts openpyxl
```

#### 2. 运行分析

```bash
python data_analysis.py
```

#### 3. 查看结果

程序运行完成后，所有图表将保存在 `output_charts/` 目录中：
- PNG格式的静态图表（用于报告和展示）
- HTML格式的交互式地图（可在浏览器中打开查看）

### 📈 输出图表列表

1. 全国历年GDP总值变化趋势
2. 全国历年人均收入与消费水平
3. 全国历年国内外旅游收入对比
4. 全国历年国内外游客数量对比
5-6. 各省GDP排名（最新年份 & 10年前）
7-8. 各省旅游外汇收入排名（最新年份 & 10年前）
9-10. 各省接待外国游客排名（最新年份 & 10年前）
11. GDP与旅游外汇收入关联性
12. GDP与接待外国游客关联性
13. 省级GDP与旅游指标相关性热力图
14-15. 各省GDP分布地图（交互式HTML）
16-17. 各省旅游外汇收入分布地图（交互式HTML）
18-19. 各省接待外国游客分布地图（交互式HTML）
20. 各省GDP增长率排名
21. 海南月度接待游客数
22. 海南月度旅游总收入

### 🔍 核心功能说明

#### 数据预处理
- 自动清理列名中的空格和特殊字符
- 智能转换数据格式（长格式/宽格式转换）
- 自动去重和数据验证
- 支持多种数据源格式

#### 可视化功能
- **时间序列图**: 展示数据随时间的变化趋势
- **柱状图**: 横向对比不同省份的数据
- **散点图**: 分析两个指标之间的关联性
- **热力图**: 展示多个指标之间的相关系数
- **地理地图**: 在中国地图上展示数据分布

### 📊 数据说明

项目使用的数据涵盖：
- **时间跨度**: 2009-2023年（部分数据）
- **空间范围**: 全国31个省级行政区
- **数据维度**: 
  - 经济指标：GDP、人均收入、消费水平
  - 旅游指标：国内/国际游客数、旅游收入、外汇收入

### 🎯 应用场景

- 经济学研究和课程设计
- 旅游业发展趋势分析
- 区域经济对比研究
- 政策效果评估
- 数据可视化教学案例

### 📝 注意事项

1. 确保 `data/` 文件夹中包含所有必需的Excel数据文件
2. 中文显示需要系统安装SimHei（黑体）字体
3. 生成地图需要网络连接（Pyecharts地图资源）
4. 建议使用Python 3.7或更高版本

### 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

### 📄 许可证

本项目仅供学习和研究使用。

---

## English Description

### 📊 Project Overview

A Python-based data visualization system for analyzing China's tourism and GDP data from 2009-2023. The system generates 22+ professional charts including time series plots, bar charts, scatter plots, heatmaps, and interactive maps.

### ✨ Key Features

- **National-level time series analysis**
  - GDP trends
  - Income vs consumption comparison
  - Domestic/international tourism revenue and visitor statistics

- **Provincial comparative analysis**
  - Provincial GDP rankings (latest year & 10-year comparison)
  - Tourism foreign exchange income rankings
  - Foreign visitor reception rankings
  - GDP growth rate rankings

- **Correlation analysis**
  - GDP vs tourism revenue scatter plots
  - GDP vs foreign visitors correlation
  - Multi-indicator correlation heatmaps

- **Geographic visualization**
  - Interactive provincial GDP distribution maps
  - Tourism revenue distribution maps
  - Foreign visitor distribution maps

- **Special analysis**
  - Hainan monthly tourism trend analysis

### 🛠️ Tech Stack

- **Python 3.7+**
- **Data Processing**: Pandas, NumPy
- **Visualization**: Matplotlib, Seaborn
- **Geographic Visualization**: Pyecharts
- **Data Source**: Excel annual statistical data

### 🚀 Quick Start

#### 1. Install Dependencies

```bash
pip install pandas matplotlib seaborn pyecharts openpyxl
```

#### 2. Run Analysis

```bash
python data_analysis.py
```

#### 3. View Results

All charts will be saved in the `output_charts/` directory:
- PNG static charts (for reports and presentations)
- HTML interactive maps (open in browser)

### 📈 Output Charts

The system generates 22+ charts covering:
- National trends (GDP, income, tourism)
- Provincial rankings and comparisons
- Correlation analyses
- Geographic distribution maps
- Growth rate analyses

### 🎯 Use Cases

- Economics research and coursework
- Tourism industry trend analysis
- Regional economic comparison studies
- Policy impact assessment
- Data visualization teaching examples

### 📝 Notes

1. Ensure all Excel data files are in the `data/` folder
2. Chinese font (SimHei) required for proper text display
3. Internet connection needed for map generation
4. Python 3.7+ recommended

### 🤝 Contributing

Issues and Pull Requests are welcome!

### 📄 License

This project is for educational and research purposes only.
