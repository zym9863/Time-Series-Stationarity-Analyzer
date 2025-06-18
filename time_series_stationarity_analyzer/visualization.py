"""
可视化模块
提供时间序列数据的各种可视化功能
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from typing import Tuple, Optional
from .stationarity import calculate_acf_pacf

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

class TimeSeriesVisualizer:
    """时间序列可视化器"""
    
    def __init__(self, theme: str = 'plotly_white'):
        """
        初始化可视化器
        
        Args:
            theme: 图表主题
        """
        self.theme = theme
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff9800',
            'info': '#17a2b8'
        }
    
    def plot_time_series(self, data: pd.Series, title: str = "时间序列图", 
                        height: int = 400) -> go.Figure:
        """
        绘制时间序列图
        
        Args:
            data: 时间序列数据
            title: 图表标题
            height: 图表高度
        
        Returns:
            Plotly图表对象
        """
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data.values,
            mode='lines',
            name='时间序列',
            line=dict(color=self.colors['primary'], width=2),
            hovertemplate='<b>时间</b>: %{x}<br><b>数值</b>: %{y:.4f}<extra></extra>'
        ))
        
        # 添加趋势线
        if len(data) > 1:
            x_numeric = np.arange(len(data))
            z = np.polyfit(x_numeric, data.values, 1)
            p = np.poly1d(z)
            
            fig.add_trace(go.Scatter(
                x=data.index,
                y=p(x_numeric),
                mode='lines',
                name='趋势线',
                line=dict(color=self.colors['danger'], width=2, dash='dash'),
                hovertemplate='<b>趋势</b>: %{y:.4f}<extra></extra>'
            ))
        
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=16)),
            xaxis_title="时间",
            yaxis_title="数值",
            template=self.theme,
            height=height,
            hovermode='x unified',
            showlegend=True
        )
        
        return fig
    
    def plot_acf_pacf(self, data: pd.Series, lags: int = 40, 
                     title: str = "自相关和偏自相关函数") -> go.Figure:
        """
        绘制ACF和PACF图
        
        Args:
            data: 时间序列数据
            lags: 滞后期数
            title: 图表标题
        
        Returns:
            Plotly图表对象
        """
        # 计算ACF和PACF
        acf_values, pacf_values = calculate_acf_pacf(data, lags)
        
        if len(acf_values) == 0 or len(pacf_values) == 0:
            # 如果计算失败，返回空图
            fig = go.Figure()
            fig.add_annotation(
                text="ACF/PACF计算失败",
                x=0.5, y=0.5,
                xref="paper", yref="paper",
                showarrow=False,
                font=dict(size=16)
            )
            return fig
        
        # 创建子图
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('自相关函数 (ACF)', '偏自相关函数 (PACF)'),
            vertical_spacing=0.1
        )
        
        # 计算置信区间
        n = len(data)
        confidence_interval = 1.96 / np.sqrt(n)
        
        # ACF图
        lags_range = list(range(len(acf_values)))
        fig.add_trace(
            go.Bar(
                x=lags_range,
                y=acf_values,
                name='ACF',
                marker_color=self.colors['primary'],
                hovertemplate='<b>滞后期</b>: %{x}<br><b>ACF</b>: %{y:.4f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # 添加置信区间线
        fig.add_hline(y=confidence_interval, line_dash="dash", 
                     line_color=self.colors['danger'], row=1, col=1)
        fig.add_hline(y=-confidence_interval, line_dash="dash", 
                     line_color=self.colors['danger'], row=1, col=1)
        
        # PACF图
        pacf_lags_range = list(range(len(pacf_values)))
        fig.add_trace(
            go.Bar(
                x=pacf_lags_range,
                y=pacf_values,
                name='PACF',
                marker_color=self.colors['secondary'],
                hovertemplate='<b>滞后期</b>: %{x}<br><b>PACF</b>: %{y:.4f}<extra></extra>'
            ),
            row=2, col=1
        )
        
        # 添加置信区间线
        fig.add_hline(y=confidence_interval, line_dash="dash", 
                     line_color=self.colors['danger'], row=2, col=1)
        fig.add_hline(y=-confidence_interval, line_dash="dash", 
                     line_color=self.colors['danger'], row=2, col=1)
        
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=16)),
            template=self.theme,
            height=600,
            showlegend=False
        )
        
        fig.update_xaxes(title_text="滞后期", row=2, col=1)
        fig.update_yaxes(title_text="ACF值", row=1, col=1)
        fig.update_yaxes(title_text="PACF值", row=2, col=1)
        
        return fig
    
    def plot_decomposition(self, data: pd.Series, 
                          title: str = "时间序列分解") -> go.Figure:
        """
        绘制时间序列分解图
        
        Args:
            data: 时间序列数据
            title: 图表标题
        
        Returns:
            Plotly图表对象
        """
        try:
            from statsmodels.tsa.seasonal import seasonal_decompose
            
            # 进行时间序列分解
            decomposition = seasonal_decompose(data, model='additive', period=min(12, len(data)//2))
            
            # 创建子图
            fig = make_subplots(
                rows=4, cols=1,
                subplot_titles=('原始序列', '趋势', '季节性', '残差'),
                vertical_spacing=0.08
            )
            
            # 原始序列
            fig.add_trace(
                go.Scatter(
                    x=data.index, y=data.values,
                    mode='lines', name='原始序列',
                    line=dict(color=self.colors['primary'])
                ),
                row=1, col=1
            )
            
            # 趋势
            fig.add_trace(
                go.Scatter(
                    x=data.index, y=decomposition.trend.values,
                    mode='lines', name='趋势',
                    line=dict(color=self.colors['secondary'])
                ),
                row=2, col=1
            )
            
            # 季节性
            fig.add_trace(
                go.Scatter(
                    x=data.index, y=decomposition.seasonal.values,
                    mode='lines', name='季节性',
                    line=dict(color=self.colors['success'])
                ),
                row=3, col=1
            )
            
            # 残差
            fig.add_trace(
                go.Scatter(
                    x=data.index, y=decomposition.resid.values,
                    mode='lines', name='残差',
                    line=dict(color=self.colors['danger'])
                ),
                row=4, col=1
            )
            
            fig.update_layout(
                title=dict(text=title, x=0.5, font=dict(size=16)),
                template=self.theme,
                height=800,
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            # 如果分解失败，返回错误信息
            fig = go.Figure()
            fig.add_annotation(
                text=f"时间序列分解失败: {str(e)}",
                x=0.5, y=0.5,
                xref="paper", yref="paper",
                showarrow=False,
                font=dict(size=16)
            )
            return fig
    
    def plot_distribution(self, data: pd.Series, 
                         title: str = "数据分布") -> go.Figure:
        """
        绘制数据分布图
        
        Args:
            data: 时间序列数据
            title: 图表标题
        
        Returns:
            Plotly图表对象
        """
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('直方图', '箱线图'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 直方图
        fig.add_trace(
            go.Histogram(
                x=data.values,
                nbinsx=30,
                name='分布',
                marker_color=self.colors['primary'],
                opacity=0.7
            ),
            row=1, col=1
        )
        
        # 箱线图
        fig.add_trace(
            go.Box(
                y=data.values,
                name='箱线图',
                marker_color=self.colors['secondary'],
                boxpoints='outliers'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=16)),
            template=self.theme,
            height=400,
            showlegend=False
        )
        
        fig.update_xaxes(title_text="数值", row=1, col=1)
        fig.update_yaxes(title_text="频次", row=1, col=1)
        fig.update_yaxes(title_text="数值", row=1, col=2)
        
        return fig
    
    def plot_rolling_statistics(self, data: pd.Series, window: int = 12,
                               title: str = "滚动统计") -> go.Figure:
        """
        绘制滚动统计图
        
        Args:
            data: 时间序列数据
            window: 滚动窗口大小
            title: 图表标题
        
        Returns:
            Plotly图表对象
        """
        # 计算滚动统计
        rolling_mean = data.rolling(window=window).mean()
        rolling_std = data.rolling(window=window).std()
        
        fig = go.Figure()
        
        # 原始数据
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data.values,
            mode='lines',
            name='原始数据',
            line=dict(color=self.colors['primary'], width=1),
            opacity=0.7
        ))
        
        # 滚动均值
        fig.add_trace(go.Scatter(
            x=rolling_mean.index,
            y=rolling_mean.values,
            mode='lines',
            name=f'滚动均值 (窗口={window})',
            line=dict(color=self.colors['secondary'], width=2)
        ))
        
        # 滚动标准差
        fig.add_trace(go.Scatter(
            x=rolling_std.index,
            y=rolling_std.values,
            mode='lines',
            name=f'滚动标准差 (窗口={window})',
            line=dict(color=self.colors['danger'], width=2),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=16)),
            xaxis_title="时间",
            yaxis=dict(title="数值", side='left'),
            yaxis2=dict(title="标准差", side='right', overlaying='y'),
            template=self.theme,
            height=400,
            hovermode='x unified'
        )
        
        return fig
    
    def compare_series(self, original: pd.Series, transformed: pd.Series,
                      labels: Tuple[str, str] = ("原始序列", "转换后序列"),
                      title: str = "序列对比") -> go.Figure:
        """
        对比两个序列
        
        Args:
            original: 原始序列
            transformed: 转换后序列
            labels: 序列标签
            title: 图表标题
        
        Returns:
            Plotly图表对象
        """
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=labels,
            vertical_spacing=0.1
        )
        
        # 原始序列
        fig.add_trace(
            go.Scatter(
                x=original.index,
                y=original.values,
                mode='lines',
                name=labels[0],
                line=dict(color=self.colors['primary'], width=2)
            ),
            row=1, col=1
        )
        
        # 转换后序列
        fig.add_trace(
            go.Scatter(
                x=transformed.index,
                y=transformed.values,
                mode='lines',
                name=labels[1],
                line=dict(color=self.colors['secondary'], width=2)
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=16)),
            template=self.theme,
            height=600,
            showlegend=False
        )
        
        fig.update_xaxes(title_text="时间", row=2, col=1)
        fig.update_yaxes(title_text="数值", row=1, col=1)
        fig.update_yaxes(title_text="数值", row=2, col=1)
        
        return fig

def create_test_report_chart(test_results: dict) -> go.Figure:
    """
    创建检验结果汇总图表
    
    Args:
        test_results: 检验结果字典
    
    Returns:
        Plotly图表对象
    """
    tests = []
    p_values = []
    conclusions = []
    colors = []
    
    # 提取检验结果
    if 'adf_test' in test_results and 'p_value' in test_results['adf_test']:
        tests.append('ADF检验')
        p_values.append(test_results['adf_test']['p_value'])
        is_stationary = test_results['adf_test']['is_stationary']
        conclusions.append('平稳' if is_stationary else '非平稳')
        colors.append('#2ca02c' if is_stationary else '#d62728')
    
    if 'kpss_test' in test_results and 'p_value' in test_results['kpss_test']:
        tests.append('KPSS检验')
        p_values.append(test_results['kpss_test']['p_value'])
        is_stationary = test_results['kpss_test']['is_stationary']
        conclusions.append('平稳' if is_stationary else '非平稳')
        colors.append('#2ca02c' if is_stationary else '#d62728')
    
    if not tests:
        fig = go.Figure()
        fig.add_annotation(
            text="无可用的检验结果",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # 创建条形图
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=tests,
        y=p_values,
        text=[f'{conclusion}<br>p={p:.4f}' for conclusion, p in zip(conclusions, p_values)],
        textposition='auto',
        marker_color=colors,
        hovertemplate='<b>%{x}</b><br>p值: %{y:.4f}<br>结论: %{text}<extra></extra>'
    ))
    
    # 添加显著性水平线
    fig.add_hline(y=0.05, line_dash="dash", line_color="red", 
                 annotation_text="α = 0.05")
    
    fig.update_layout(
        title=dict(text="平稳性检验结果汇总", x=0.5, font=dict(size=16)),
        xaxis_title="检验方法",
        yaxis_title="p值",
        template='plotly_white',
        height=400
    )
    
    return fig
