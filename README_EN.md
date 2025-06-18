[🇨🇳 中文](README.md) | [🇺🇸 English](README_EN.md)

# Time Series Stationarity Analyzer

A Python and Streamlit-based time series stationarity analysis tool that provides automated testing and interactive visualization features.

## Features

- 📊 **Automated Stationarity Tests**: Support for multiple testing methods including ADF, KPSS, PP
- 📈 **Interactive Visualization**: Time series plots, ACF/PACF charts
- 🔄 **Differencing Operations**: First-order and second-order differencing with real-time results
- 📋 **Report Generation**: Automatic generation of detailed analysis reports
- 🎯 **User-Friendly**: Intuitive web interface with CSV file upload support

## Installation and Usage

### Using uv Environment Manager

```bash
# Install uv (if not already installed)
pip install uv

# Create virtual environment and install dependencies
uv sync

# Run the application
uv run streamlit run app.py
```

### Manual Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## Usage Instructions

1. Upload CSV format time series data
2. Select time column and value column
3. View visualization and stationarity test results of original data
4. Apply differencing operations if needed
5. Download analysis report

## Project Structure

```
Time-Series-Stationarity-Analyzer/
├── app.py                 # Main Streamlit application
├── time_series_stationarity_analyzer/
│   ├── __init__.py
│   ├── stationarity.py    # Stationarity testing module
│   ├── visualization.py   # Visualization module
│   └── utils.py          # Utility functions
├── data/                  # Sample data
├── pyproject.toml         # Project configuration
└── README.md
```

## Tech Stack

- **Python 3.9+**
- **Streamlit**: Web interface framework
- **pandas**: Data processing
- **statsmodels**: Statistical analysis
- **matplotlib/plotly**: Data visualization
- **uv**: Python package manager
