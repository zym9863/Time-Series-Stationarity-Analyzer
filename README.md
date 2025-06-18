[🇨🇳 中文](README.md) | [🇺🇸 English](README_EN.md)

# 时序数据平稳性分析器

一个基于 Python 和 Streamlit 的时间序列平稳性分析工具，提供自动化检验和交互式可视化功能。

## 功能特性

- 📊 **自动化平稳性检验**：支持 ADF、KPSS、PP 等多种检验方法
- 📈 **交互式可视化**：时间序列图、ACF/PACF 图表
- 🔄 **差分处理**：一阶、二阶差分处理和实时结果展示
- 📋 **报告生成**：自动生成详细的分析报告
- 🎯 **用户友好**：直观的 Web 界面，支持 CSV 文件上传

## 安装和运行

### 使用 uv 管理环境

```bash
# 安装 uv（如果尚未安装）
pip install uv

# 创建虚拟环境并安装依赖
uv sync

# 运行应用
uv run streamlit run app.py
```

### 手动安装

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行应用
streamlit run app.py
```

## 使用说明

1. 上传 CSV 格式的时间序列数据
2. 选择时间列和数值列
3. 查看原始数据的可视化和平稳性检验结果
4. 如需要，进行差分处理
5. 下载分析报告

## 项目结构

```
Time-Series-Stationarity-Analyzer/
├── app.py                 # Streamlit主应用
├── time_series_stationarity_analyzer/
│   ├── __init__.py
│   ├── stationarity.py    # 平稳性检验模块
│   ├── visualization.py   # 可视化模块
│   └── utils.py          # 工具函数
├── data/                  # 示例数据
├── pyproject.toml         # 项目配置
└── README.md
```

## 技术栈

- **Python 3.9+**
- **Streamlit**: Web 界面框架
- **pandas**: 数据处理
- **statsmodels**: 统计分析
- **matplotlib/plotly**: 数据可视化
- **uv**: Python 包管理器
