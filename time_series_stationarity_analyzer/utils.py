"""
工具函数模块
提供数据处理、报告生成等辅助功能
"""

import pandas as pd
import numpy as np
import io
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import streamlit as st

def load_data_from_file(uploaded_file) -> Optional[pd.DataFrame]:
    """
    从上传的文件加载数据
    
    Args:
        uploaded_file: Streamlit上传的文件对象
    
    Returns:
        加载的DataFrame或None
    """
    try:
        if uploaded_file is None:
            return None
        
        # 根据文件扩展名选择读取方法
        file_extension = uploaded_file.name.lower().split('.')[-1]
        
        if file_extension == 'csv':
            # 尝试不同的编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
            for encoding in encodings:
                try:
                    uploaded_file.seek(0)  # 重置文件指针
                    df = pd.read_csv(uploaded_file, encoding=encoding)
                    return df
                except UnicodeDecodeError:
                    continue
            
            # 如果所有编码都失败，使用默认编码并报错
            st.error("无法读取CSV文件，请检查文件编码")
            return None
            
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file)
            return df
        else:
            st.error(f"不支持的文件格式: {file_extension}")
            return None
            
    except Exception as e:
        st.error(f"文件读取失败: {str(e)}")
        return None

def validate_time_series_data(df: pd.DataFrame, 
                             time_col: str, 
                             value_col: str) -> Tuple[bool, str, Optional[pd.Series]]:
    """
    验证时间序列数据的有效性
    
    Args:
        df: 数据框
        time_col: 时间列名
        value_col: 数值列名
    
    Returns:
        (是否有效, 错误信息, 时间序列数据)
    """
    try:
        # 检查列是否存在
        if time_col not in df.columns:
            return False, f"时间列 '{time_col}' 不存在", None
        
        if value_col not in df.columns:
            return False, f"数值列 '{value_col}' 不存在", None
        
        # 检查数据是否为空
        if df.empty:
            return False, "数据为空", None
        
        # 尝试转换时间列
        try:
            time_series = pd.to_datetime(df[time_col])
        except Exception as e:
            return False, f"时间列转换失败: {str(e)}", None
        
        # 检查数值列
        try:
            values = pd.to_numeric(df[value_col], errors='coerce')
            if values.isna().all():
                return False, "数值列包含无效数据", None
        except Exception as e:
            return False, f"数值列转换失败: {str(e)}", None
        
        # 创建时间序列
        ts_data = pd.Series(values.values, index=time_series, name=value_col)
        ts_data = ts_data.dropna()
        
        if len(ts_data) < 10:
            return False, "有效数据点太少（少于10个）", None
        
        return True, "", ts_data
        
    except Exception as e:
        return False, f"数据验证失败: {str(e)}", None

def generate_analysis_report(test_results: Dict[str, Any], 
                           data_info: Dict[str, Any]) -> str:
    """
    生成分析报告
    
    Args:
        test_results: 检验结果
        data_info: 数据信息
    
    Returns:
        分析报告文本
    """
    report = []
    
    # 报告标题
    report.append("# 时间序列平稳性分析报告")
    report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # 数据概览
    report.append("## 数据概览")
    if 'basic_statistics' in test_results:
        stats = test_results['basic_statistics']
        report.append(f"- **数据点数量**: {stats.get('count', 'N/A')}")
        report.append(f"- **均值**: {stats.get('mean', 0):.4f}")
        report.append(f"- **标准差**: {stats.get('std', 0):.4f}")
        report.append(f"- **最小值**: {stats.get('min', 0):.4f}")
        report.append(f"- **最大值**: {stats.get('max', 0):.4f}")
        report.append(f"- **偏度**: {stats.get('skewness', 0):.4f}")
        report.append(f"- **峰度**: {stats.get('kurtosis', 0):.4f}")
    report.append("")
    
    # 平稳性检验结果
    report.append("## 平稳性检验结果")
    
    # 综合结论
    if 'overall_conclusion' in test_results:
        report.append(f"**综合结论**: {test_results['overall_conclusion']}")
        report.append("")
    
    # ADF检验
    if 'adf_test' in test_results:
        adf = test_results['adf_test']
        if 'error' not in adf:
            report.append("### ADF检验 (增强迪基-富勒检验)")
            report.append(f"- **检验统计量**: {adf['test_statistic']:.4f}")
            report.append(f"- **p值**: {adf['p_value']:.4f}")
            report.append(f"- **使用滞后期**: {adf['used_lag']}")
            report.append(f"- **观测值数量**: {adf['n_obs']}")
            report.append("- **临界值**:")
            for level, value in adf['critical_values'].items():
                report.append(f"  - {level}: {value:.4f}")
            report.append(f"- **结论**: {adf['conclusion']}")
            report.append("")
    
    # KPSS检验
    if 'kpss_test' in test_results:
        kpss = test_results['kpss_test']
        if 'error' not in kpss:
            report.append("### KPSS检验")
            report.append(f"- **检验统计量**: {kpss['test_statistic']:.4f}")
            report.append(f"- **p值**: {kpss['p_value']:.4f}")
            report.append(f"- **使用滞后期**: {kpss['used_lag']}")
            report.append("- **临界值**:")
            for level, value in kpss['critical_values'].items():
                report.append(f"  - {level}: {value:.4f}")
            report.append(f"- **结论**: {kpss['conclusion']}")
            report.append("")
    
    # Ljung-Box检验
    if 'ljung_box_test' in test_results:
        ljung = test_results['ljung_box_test']
        if 'error' not in ljung:
            report.append("### Ljung-Box检验 (残差独立性)")
            report.append(f"- **检验统计量**: {ljung['test_statistic']:.4f}")
            report.append(f"- **p值**: {ljung['p_value']:.4f}")
            report.append(f"- **滞后期**: {ljung['lags']}")
            report.append(f"- **结论**: {ljung['conclusion']}")
            report.append("")
    
    
    # 技术说明
    report.append("## 技术说明")
    report.append("### 检验方法说明")
    report.append("- **ADF检验**: 原假设为序列存在单位根（非平稳），p值<0.05时拒绝原假设，认为序列平稳")
    report.append("- **KPSS检验**: 原假设为序列平稳，p值>0.05时接受原假设，认为序列平稳")
    report.append("- **Ljung-Box检验**: 检验残差是否存在自相关，p值>0.05时认为残差独立")
    report.append("")
    report.append("### 平稳性的重要性")
    report.append("平稳时间序列具有以下特征：")
    report.append("- 均值不随时间变化")
    report.append("- 方差保持常数")
    report.append("- 协方差只依赖于时间间隔，不依赖于时间本身")
    report.append("")
    report.append("非平稳序列可能导致虚假回归等问题，建议通过差分、对数变换等方法使序列平稳。")
    
    return "\n".join(report)

def create_sample_data() -> pd.DataFrame:
    """
    创建示例数据
    
    Returns:
        示例时间序列数据
    """
    # 生成日期范围
    dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
    
    # 生成几种不同类型的时间序列
    np.random.seed(42)
    
    # 1. 带趋势的非平稳序列
    trend = np.linspace(100, 200, len(dates))
    noise = np.random.normal(0, 10, len(dates))
    non_stationary = trend + noise
    
    # 2. 平稳序列（围绕均值波动）
    stationary = np.random.normal(50, 5, len(dates))
    
    # 3. 带季节性的序列
    seasonal = 100 + 20 * np.sin(2 * np.pi * np.arange(len(dates)) / 365.25) + np.random.normal(0, 5, len(dates))
    
    # 4. 随机游走（非平稳）
    random_walk = np.cumsum(np.random.normal(0, 1, len(dates))) + 100
    
    sample_data = pd.DataFrame({
        'date': dates,
        'trend_series': non_stationary,
        'stationary_series': stationary,
        'seasonal_series': seasonal,
        'random_walk': random_walk
    })
    
    return sample_data

def format_number(value: float, decimals: int = 4) -> str:
    """
    格式化数字显示
    
    Args:
        value: 数值
        decimals: 小数位数
    
    Returns:
        格式化后的字符串
    """
    if pd.isna(value):
        return "N/A"
    
    if abs(value) < 1e-4:
        return f"{value:.2e}"
    else:
        return f"{value:.{decimals}f}"

def get_data_summary(data: pd.Series) -> Dict[str, Any]:
    """
    获取数据摘要信息
    
    Args:
        data: 时间序列数据
    
    Returns:
        数据摘要字典
    """
    return {
        'count': len(data),
        'start_date': data.index.min() if len(data) > 0 else None,
        'end_date': data.index.max() if len(data) > 0 else None,
        'frequency': infer_frequency(data),
        'missing_values': data.isna().sum(),
        'missing_percentage': (data.isna().sum() / len(data)) * 100 if len(data) > 0 else 0
    }

def infer_frequency(data: pd.Series) -> str:
    """
    推断时间序列频率
    
    Args:
        data: 时间序列数据
    
    Returns:
        频率字符串
    """
    try:
        if len(data) < 2:
            return "Unknown"
        
        # 计算时间间隔
        time_diffs = pd.Series(data.index).diff().dropna()
        most_common_diff = time_diffs.mode()[0] if len(time_diffs.mode()) > 0 else time_diffs.median()
        
        # 判断频率
        if most_common_diff <= pd.Timedelta(days=1):
            return "Daily"
        elif most_common_diff <= pd.Timedelta(days=7):
            return "Weekly"
        elif most_common_diff <= pd.Timedelta(days=31):
            return "Monthly"
        elif most_common_diff <= pd.Timedelta(days=92):
            return "Quarterly"
        elif most_common_diff <= pd.Timedelta(days=366):
            return "Yearly"
        else:
            return "Irregular"
    
    except Exception:
        return "Unknown"

def export_results_to_csv(data: pd.Series, test_results: Dict[str, Any]) -> str:
    """
    将结果导出为CSV格式
    
    Args:
        data: 时间序列数据
        test_results: 检验结果
    
    Returns:
        CSV格式的字符串
    """
    # 创建结果DataFrame
    results_data = []
    
    # 基本统计信息
    if 'basic_statistics' in test_results:
        stats = test_results['basic_statistics']
        for key, value in stats.items():
            results_data.append({
                'Category': 'Basic Statistics',
                'Metric': key,
                'Value': value,
                'Description': get_stat_description(key)
            })
    
    # ADF检验结果
    if 'adf_test' in test_results and 'error' not in test_results['adf_test']:
        adf = test_results['adf_test']
        results_data.append({
            'Category': 'ADF Test',
            'Metric': 'Test Statistic',
            'Value': adf['test_statistic'],
            'Description': 'ADF test statistic'
        })
        results_data.append({
            'Category': 'ADF Test',
            'Metric': 'P-Value',
            'Value': adf['p_value'],
            'Description': 'ADF test p-value'
        })
        results_data.append({
            'Category': 'ADF Test',
            'Metric': 'Is Stationary',
            'Value': adf['is_stationary'],
            'Description': 'Whether series is stationary (ADF test)'
        })
    
    # KPSS检验结果
    if 'kpss_test' in test_results and 'error' not in test_results['kpss_test']:
        kpss = test_results['kpss_test']
        results_data.append({
            'Category': 'KPSS Test',
            'Metric': 'Test Statistic',
            'Value': kpss['test_statistic'],
            'Description': 'KPSS test statistic'
        })
        results_data.append({
            'Category': 'KPSS Test',
            'Metric': 'P-Value',
            'Value': kpss['p_value'],
            'Description': 'KPSS test p-value'
        })
        results_data.append({
            'Category': 'KPSS Test',
            'Metric': 'Is Stationary',
            'Value': kpss['is_stationary'],
            'Description': 'Whether series is stationary (KPSS test)'
        })
    
    # 创建DataFrame并转换为CSV
    results_df = pd.DataFrame(results_data)
    
    # 将原始数据也包含在内
    data_df = pd.DataFrame({
        'Date': data.index,
        'Value': data.values
    })
    
    # 使用StringIO创建CSV
    output = io.StringIO()
    
    # 写入分析结果
    output.write("=== STATIONARITY ANALYSIS RESULTS ===\n")
    results_df.to_csv(output, index=False)
    
    output.write("\n\n=== ORIGINAL DATA ===\n")
    data_df.to_csv(output, index=False)
    
    return output.getvalue()

def get_stat_description(stat_name: str) -> str:
    """
    获取统计量描述
    
    Args:
        stat_name: 统计量名称
    
    Returns:
        统计量描述
    """
    descriptions = {
        'mean': 'Average value of the series',
        'std': 'Standard deviation',
        'variance': 'Variance of the series',
        'skewness': 'Measure of asymmetry',
        'kurtosis': 'Measure of tail heaviness',
        'min': 'Minimum value',
        'max': 'Maximum value',
        'median': 'Median value',
        'count': 'Number of observations'
    }
    return descriptions.get(stat_name, 'Statistical measure')
