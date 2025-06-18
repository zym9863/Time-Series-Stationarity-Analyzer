@echo off
echo 正在启动时间序列平稳性分析器...
echo.
echo 请确保已安装 uv 包管理器
echo 如果尚未安装，请运行: pip install uv
echo.
uv sync
echo.
echo 启动 Streamlit 应用...
uv run streamlit run app.py
pause
