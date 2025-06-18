"""
时间序列平稳性分析器 - Streamlit主应用
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io
import warnings
warnings.filterwarnings('ignore')

# 导入自定义模块
from time_series_stationarity_analyzer.stationarity import StationarityAnalyzer
from time_series_stationarity_analyzer.visualization import TimeSeriesVisualizer, create_test_report_chart
from time_series_stationarity_analyzer.utils import (
    load_data_from_file, 
    validate_time_series_data, 
    generate_analysis_report,
    create_sample_data,
    get_data_summary,
    export_results_to_csv
)

# 页面配置
st.set_page_config(
    page_title="时间序列平稳性分析器",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stAlert > div {
        padding: 1rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """主应用函数"""
    
    # 主标题
    st.markdown('<div class="main-header">📈 时间序列平稳性分析器</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">专业的时间序列平稳性检验与可视化分析工具</div>', unsafe_allow_html=True)
    
    # 初始化会话状态
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'visualizer' not in st.session_state:
        st.session_state.visualizer = TimeSeriesVisualizer()
    
    # 侧边栏
    with st.sidebar:
        st.header("🔧 控制面板")
        
        # 数据源选择
        data_source = st.radio(
            "选择数据源",
            ["上传文件", "使用示例数据"],
            index=0
        )
        
        # 数据加载
        if data_source == "上传文件":
            uploaded_file = st.file_uploader(
                "上传CSV或Excel文件",
                type=['csv', 'xlsx', 'xls'],
                help="支持CSV和Excel格式，请确保包含时间列和数值列"
            )
            
            if uploaded_file is not None:
                df = load_data_from_file(uploaded_file)
                if df is not None:
                    st.success(f"文件加载成功！数据维度: {df.shape}")
                    
                    # 列选择
                    time_col = st.selectbox("选择时间列", df.columns)
                    value_col = st.selectbox("选择数值列", df.columns)
                    
                    if st.button("验证数据", type="primary"):
                        is_valid, error_msg, ts_data = validate_time_series_data(df, time_col, value_col)
                        if is_valid:
                            st.session_state.data = ts_data
                            st.success("数据验证成功！")
                        else:
                            st.error(f"数据验证失败: {error_msg}")
        
        else:  # 使用示例数据
            sample_data = create_sample_data()
            st.info("使用内置示例数据集")
            
            series_options = {
                "带趋势序列（非平稳）": "trend_series",
                "平稳序列": "stationary_series", 
                "季节性序列": "seasonal_series",
                "随机游走（非平稳）": "random_walk"
            }
            
            selected_series = st.selectbox("选择示例序列", list(series_options.keys()))
            
            if st.button("加载示例数据", type="primary"):
                series_col = series_options[selected_series]
                ts_data = pd.Series(
                    sample_data[series_col].values,
                    index=sample_data['date'],
                    name=selected_series
                )
                st.session_state.data = ts_data
                st.success(f"示例数据加载成功：{selected_series}")
        
        # 分析选项
        if st.session_state.data is not None:
            st.subheader("📊 分析选项")
            
            if st.button("开始分析", type="primary"):
                with st.spinner("正在进行平稳性分析..."):
                    analyzer = StationarityAnalyzer(st.session_state.data)
                    results = analyzer.comprehensive_test()
                    st.session_state.analysis_results = results
                st.success("分析完成！")
    
    # 主内容区域
    if st.session_state.data is not None:
        # 数据概览
        st.header("📋 数据概览")
        
        col1, col2, col3, col4 = st.columns(4)
        
        data_summary = get_data_summary(st.session_state.data)
        
        with col1:
            st.metric("数据点数量", f"{data_summary['count']:,}")
        with col2:
            st.metric("开始日期", data_summary['start_date'].strftime('%Y-%m-%d') if data_summary['start_date'] else "N/A")
        with col3:
            st.metric("结束日期", data_summary['end_date'].strftime('%Y-%m-%d') if data_summary['end_date'] else "N/A")
        with col4:
            st.metric("数据频率", data_summary['frequency'])
        
        # 基本统计信息
        with st.expander("📊 基本统计信息", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("均值", f"{st.session_state.data.mean():.4f}")
                st.metric("最小值", f"{st.session_state.data.min():.4f}")
                st.metric("偏度", f"{st.session_state.data.skew():.4f}")
            
            with col2:
                st.metric("标准差", f"{st.session_state.data.std():.4f}")
                st.metric("最大值", f"{st.session_state.data.max():.4f}")
                st.metric("峰度", f"{st.session_state.data.kurtosis():.4f}")
        
        # 数据可视化
        st.header("📈 数据可视化")
        
        # 时间序列图
        fig_ts = st.session_state.visualizer.plot_time_series(
            st.session_state.data, 
            title="原始时间序列"
        )
        st.plotly_chart(fig_ts, use_container_width=True)
        
        # 其他图表选项
        viz_tabs = st.tabs(["📊 分布图", "📈 滚动统计", "🔄 ACF/PACF", "🌊 序列分解"])
        
        with viz_tabs[0]:
            fig_dist = st.session_state.visualizer.plot_distribution(st.session_state.data)
            st.plotly_chart(fig_dist, use_container_width=True)
        
        with viz_tabs[1]:
            window_size = st.slider("滚动窗口大小", 5, 50, 12)
            fig_rolling = st.session_state.visualizer.plot_rolling_statistics(
                st.session_state.data, window=window_size
            )
            st.plotly_chart(fig_rolling, use_container_width=True)
        
        with viz_tabs[2]:
            lags = st.slider("滞后期数", 10, 100, 40)
            fig_acf_pacf = st.session_state.visualizer.plot_acf_pacf(
                st.session_state.data, lags=lags
            )
            st.plotly_chart(fig_acf_pacf, use_container_width=True)
        
        with viz_tabs[3]:
            fig_decomp = st.session_state.visualizer.plot_decomposition(st.session_state.data)
            st.plotly_chart(fig_decomp, use_container_width=True)
        
        # 平稳性检验结果
        if st.session_state.analysis_results is not None:
            st.header("🔍 平稳性检验结果")
            
            # 综合结论
            conclusion = st.session_state.analysis_results.get('overall_conclusion', '分析中...')
            is_stationary = st.session_state.analysis_results.get('is_stationary', None)
            
            if is_stationary is True:
                st.markdown(f'<div class="success-box"><strong>综合结论</strong>: {conclusion}</div>', unsafe_allow_html=True)
            elif is_stationary is False:
                st.markdown(f'<div class="warning-box"><strong>综合结论</strong>: {conclusion}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="error-box"><strong>综合结论</strong>: {conclusion}</div>', unsafe_allow_html=True)
            
            # 检验结果图表
            fig_results = create_test_report_chart(st.session_state.analysis_results)
            st.plotly_chart(fig_results, use_container_width=True)
            
            # 详细结果
            result_tabs = st.tabs(["🔬 ADF检验", "📊 KPSS检验", "🎯 Ljung-Box检验"])
            
            with result_tabs[0]:
                adf_result = st.session_state.analysis_results.get('adf_test', {})
                if 'error' not in adf_result:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("检验统计量", f"{adf_result.get('test_statistic', 0):.4f}")
                        st.metric("p值", f"{adf_result.get('p_value', 0):.4f}")
                    with col2:
                        st.metric("使用滞后期", adf_result.get('used_lag', 0))
                        st.metric("观测值数量", adf_result.get('n_obs', 0))
                    
                    st.text_area(
                        "详细解释",
                        adf_result.get('interpretation', ''),
                        height=200,
                        disabled=True
                    )
                else:
                    st.error(adf_result.get('error', '检验失败'))
            
            with result_tabs[1]:
                kpss_result = st.session_state.analysis_results.get('kpss_test', {})
                if 'error' not in kpss_result:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("检验统计量", f"{kpss_result.get('test_statistic', 0):.4f}")
                        st.metric("p值", f"{kpss_result.get('p_value', 0):.4f}")
                    with col2:
                        st.metric("使用滞后期", kpss_result.get('used_lag', 0))
                    
                    st.text_area(
                        "详细解释",
                        kpss_result.get('interpretation', ''),
                        height=200,
                        disabled=True
                    )
                else:
                    st.error(kpss_result.get('error', '检验失败'))
            
            with result_tabs[2]:
                ljung_result = st.session_state.analysis_results.get('ljung_box_test', {})
                if 'error' not in ljung_result:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("检验统计量", f"{ljung_result.get('test_statistic', 0):.4f}")
                        st.metric("p值", f"{ljung_result.get('p_value', 0):.4f}")
                    with col2:
                        st.metric("滞后期", ljung_result.get('lags', 0))
                    
                    st.write(f"**结论**: {ljung_result.get('conclusion', '未知')}")
                else:
                    st.error(ljung_result.get('error', '检验失败'))
        
        # 差分处理
        st.header("🔄 差分处理")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            diff_order = st.selectbox("差分阶数", [1, 2], index=0)
            
            if st.button("执行差分", type="secondary"):
                analyzer = StationarityAnalyzer(st.session_state.data)
                differenced_data = analyzer.difference_series(order=diff_order)
                
                # 对差分后的数据进行分析
                diff_analyzer = StationarityAnalyzer(differenced_data)
                diff_results = diff_analyzer.comprehensive_test()
                
                # 存储差分结果
                st.session_state.differenced_data = differenced_data
                st.session_state.diff_results = diff_results
                st.session_state.diff_order = diff_order
        
        with col2:
            if hasattr(st.session_state, 'differenced_data'):
                st.success(f"已执行{st.session_state.diff_order}阶差分")
                
                # 显示差分后的结果
                diff_conclusion = st.session_state.diff_results.get('overall_conclusion', '分析中...')
                is_diff_stationary = st.session_state.diff_results.get('is_stationary', None)
                
                if is_diff_stationary:
                    st.success(f"差分后结论: {diff_conclusion}")
                else:
                    st.warning(f"差分后结论: {diff_conclusion}")
        
        # 差分对比图
        if hasattr(st.session_state, 'differenced_data'):
            fig_compare = st.session_state.visualizer.compare_series(
                st.session_state.data,
                st.session_state.differenced_data,
                labels=("原始序列", f"{st.session_state.diff_order}阶差分序列")
            )
            st.plotly_chart(fig_compare, use_container_width=True)
        
        # 报告生成和下载
        if st.session_state.analysis_results is not None:
            st.header("📄 分析报告")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("生成报告", type="secondary"):
                    data_info = get_data_summary(st.session_state.data)
                    report_text = generate_analysis_report(st.session_state.analysis_results, data_info)
                    st.session_state.report = report_text
            
            with col2:
                if st.button("导出CSV", type="secondary"):
                    csv_data = export_results_to_csv(st.session_state.data, st.session_state.analysis_results)
                    st.session_state.csv_export = csv_data
            
            # 显示报告
            if hasattr(st.session_state, 'report'):
                st.download_button(
                    label="下载Markdown报告",
                    data=st.session_state.report,
                    file_name=f"stationarity_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
                
                with st.expander("预览报告", expanded=False):
                    st.markdown(st.session_state.report)
            
            # CSV下载
            if hasattr(st.session_state, 'csv_export'):
                st.download_button(
                    label="下载CSV数据",
                    data=st.session_state.csv_export,
                    file_name=f"stationarity_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    else:
        # 欢迎页面
        st.info("👆 请从左侧面板上传数据文件或选择示例数据开始分析")
        
        # 功能介绍
        st.header("🌟 功能特性")
        
        features = [
            ("📊 自动化平稳性检验", "支持ADF、KPSS、Ljung-Box等多种检验方法"),
            ("📈 交互式可视化", "时间序列图、ACF/PACF图、分布图等多种图表"),
            ("🔄 差分处理", "一阶、二阶差分处理和实时结果展示"),
            ("📋 报告生成", "自动生成详细的分析报告，支持下载"),
            ("🎯 用户友好", "直观的Web界面，支持多种文件格式")
        ]
        
        for title, desc in features:
            st.markdown(f"**{title}**: {desc}")
        
        # 使用说明
        with st.expander("📖 使用说明", expanded=False):
            st.markdown("""
            ### 如何使用本工具：
            
            1. **数据准备**
               - 准备包含时间列和数值列的CSV或Excel文件
               - 确保时间列格式正确（如：2023-01-01、2023/1/1等）
               - 数值列应为数字类型
            
            2. **数据上传**
               - 点击左侧"上传文件"选择您的数据文件
               - 或选择"使用示例数据"体验功能
            
            3. **数据验证**
               - 选择正确的时间列和数值列
               - 点击"验证数据"确认数据格式正确
            
            4. **开始分析**
               - 点击"开始分析"执行平稳性检验
               - 查看各种可视化图表和检验结果
            
            5. **差分处理**
               - 如果序列非平稳，可尝试差分处理
               - 比较差分前后的结果
            
            6. **导出结果**
               - 生成并下载分析报告
               - 导出CSV格式的详细数据
            """)

if __name__ == "__main__":
    main()
