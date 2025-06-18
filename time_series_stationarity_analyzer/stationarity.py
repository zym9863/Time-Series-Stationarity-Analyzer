"""
平稳性检验模块
包含各种时间序列平稳性检验方法
"""

import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller, kpss, acf, pacf
from statsmodels.stats.diagnostic import acorr_ljungbox
from scipy import stats
from typing import Dict, Tuple, Any
import warnings
warnings.filterwarnings('ignore')


class StationarityAnalyzer:
    """时间序列平稳性分析器"""
    
    def __init__(self, data: pd.Series):
        """
        初始化分析器
        
        Args:
            data: 时间序列数据
        """
        self.data = data.dropna()
        self.results = {}
    
    def adf_test(self, maxlag: int = None, regression: str = 'c') -> Dict[str, Any]:
        """
        增强迪基-富勒检验 (Augmented Dickey-Fuller Test)
        
        Args:
            maxlag: 最大滞后阶数
            regression: 回归类型 ('c', 'ct', 'ctt', 'nc')
        
        Returns:
            检验结果字典
        """
        try:
            adf_result = adfuller(self.data, maxlag=maxlag, regression=regression)
            
            result = {
                'test_name': 'ADF检验 (增强迪基-富勒检验)',
                'test_statistic': adf_result[0],
                'p_value': adf_result[1],
                'critical_values': adf_result[4],
                'used_lag': adf_result[2],
                'n_obs': adf_result[3],
                'is_stationary': adf_result[1] < 0.05,
                'conclusion': '时间序列是平稳的' if adf_result[1] < 0.05 else '时间序列不是平稳的',
                'interpretation': self._interpret_adf(adf_result)
            }
            
            self.results['adf'] = result
            return result
            
        except Exception as e:
            return {
                'test_name': 'ADF检验',
                'error': f'检验失败: {str(e)}',
                'is_stationary': None
            }
    
    def kpss_test(self, regression: str = 'c', nlags: str = 'auto') -> Dict[str, Any]:
        """
        KPSS检验 (Kwiatkowski-Phillips-Schmidt-Shin Test)
        
        Args:
            regression: 回归类型 ('c' or 'ct')
            nlags: 滞后阶数选择方法
        
        Returns:
            检验结果字典
        """
        try:
            kpss_result = kpss(self.data, regression=regression, nlags=nlags)
            
            result = {
                'test_name': 'KPSS检验',
                'test_statistic': kpss_result[0],
                'p_value': kpss_result[1],
                'critical_values': kpss_result[3],
                'used_lag': kpss_result[2],
                'is_stationary': kpss_result[1] > 0.05,
                'conclusion': '时间序列是平稳的' if kpss_result[1] > 0.05 else '时间序列不是平稳的',
                'interpretation': self._interpret_kpss(kpss_result)
            }
            
            self.results['kpss'] = result
            return result
            
        except Exception as e:
            return {
                'test_name': 'KPSS检验',
                'error': f'检验失败: {str(e)}',
                'is_stationary': None
            }
    
    def ljung_box_test(self, lags: int = 10) -> Dict[str, Any]:
        """
        Ljung-Box检验 (残差独立性检验)
        
        Args:
            lags: 滞后阶数
        
        Returns:
            检验结果字典
        """
        try:
            lb_result = acorr_ljungbox(self.data, lags=lags, return_df=True)
            
            # 取最后一个滞后期的结果
            last_lag = lb_result.iloc[-1]
            
            result = {
                'test_name': 'Ljung-Box检验',
                'test_statistic': last_lag['lb_stat'],
                'p_value': last_lag['lb_pvalue'],
                'lags': lags,
                'is_independent': last_lag['lb_pvalue'] > 0.05,
                'conclusion': '残差是独立的' if last_lag['lb_pvalue'] > 0.05 else '残差存在自相关',
                'full_results': lb_result
            }
            
            self.results['ljung_box'] = result
            return result
            
        except Exception as e:
            return {
                'test_name': 'Ljung-Box检验',
                'error': f'检验失败: {str(e)}',
                'is_independent': None
            }
    
    def comprehensive_test(self) -> Dict[str, Any]:
        """
        综合平稳性检验
        
        Returns:
            综合检验结果
        """
        # 执行各种检验
        adf_result = self.adf_test()
        kpss_result = self.kpss_test()
        ljung_result = self.ljung_box_test()
        
        # 计算基本统计量
        basic_stats = self._calculate_basic_stats()
        
        # 综合判断
        stationarity_votes = []
        if adf_result.get('is_stationary') is not None:
            stationarity_votes.append(adf_result['is_stationary'])
        if kpss_result.get('is_stationary') is not None:
            stationarity_votes.append(kpss_result['is_stationary'])
        
        if stationarity_votes:
            overall_stationary = sum(stationarity_votes) >= len(stationarity_votes) / 2
        else:
            overall_stationary = None
        
        comprehensive_result = {
            'overall_conclusion': self._get_overall_conclusion(adf_result, kpss_result),
            'is_stationary': overall_stationary,
            'adf_test': adf_result,
            'kpss_test': kpss_result,
            'ljung_box_test': ljung_result,
            'basic_statistics': basic_stats
        }
        
        self.results['comprehensive'] = comprehensive_result
        return comprehensive_result
    
    def difference_series(self, order: int = 1) -> pd.Series:
        """
        对时间序列进行差分
        
        Args:
            order: 差分阶数
        
        Returns:
            差分后的序列
        """
        differenced = self.data.copy()
        for i in range(order):
            differenced = differenced.diff().dropna()
        return differenced
    
    def _interpret_adf(self, adf_result: Tuple) -> str:
        """解释ADF检验结果"""
        # ADF检验结果包含：统计量, p值, 使用的滞后期, 观测值数量, 临界值, (可选)回归结果
        stat = adf_result[0]
        p_value = adf_result[1]
        critical_values = adf_result[4]
        
        interpretation = f"检验统计量: {stat:.4f}\n"
        interpretation += f"p值: {p_value:.4f}\n"
        interpretation += "临界值:\n"
        
        for key, value in critical_values.items():
            comparison = "通过" if stat < value else "未通过"
            interpretation += f"  {key}: {value:.4f} ({comparison})\n"
        
        if p_value < 0.05:
            interpretation += "\n结论: 拒绝原假设，序列是平稳的"
        else:
            interpretation += "\n结论: 无法拒绝原假设，序列可能存在单位根（非平稳）"
        
        return interpretation
    
    def _interpret_kpss(self, kpss_result: Tuple) -> str:
        """解释KPSS检验结果"""
        # KPSS检验结果包含：统计量, p值, 使用的滞后期, 临界值
        stat = kpss_result[0]
        p_value = kpss_result[1]
        critical_values = kpss_result[3]
        
        interpretation = f"检验统计量: {stat:.4f}\n"
        interpretation += f"p值: {p_value:.4f}\n"
        interpretation += "临界值:\n"
        
        for key, value in critical_values.items():
            comparison = "通过" if stat < value else "未通过"
            interpretation += f"  {key}: {value:.4f} ({comparison})\n"
        
        if p_value > 0.05:
            interpretation += "\n结论: 无法拒绝原假设，序列是平稳的"
        else:
            interpretation += "\n结论: 拒绝原假设，序列是非平稳的"
        
        return interpretation
    
    def _calculate_basic_stats(self) -> Dict[str, float]:
        """计算基本统计量"""
        return {
            'mean': float(self.data.mean()),
            'std': float(self.data.std()),
            'variance': float(self.data.var()),
            'skewness': float(stats.skew(self.data)),
            'kurtosis': float(stats.kurtosis(self.data)),
            'min': float(self.data.min()),
            'max': float(self.data.max()),
            'median': float(self.data.median()),
            'count': len(self.data)
        }
    
    def _get_overall_conclusion(self, adf_result: Dict, kpss_result: Dict) -> str:
        """获取综合结论"""
        adf_stationary = adf_result.get('is_stationary')
        kpss_stationary = kpss_result.get('is_stationary')
        
        if adf_stationary is None and kpss_stationary is None:
            return "检验失败，无法判断平稳性"
        elif adf_stationary is None:
            return f"基于KPSS检验: {'平稳' if kpss_stationary else '非平稳'}"
        elif kpss_stationary is None:
            return f"基于ADF检验: {'平稳' if adf_stationary else '非平稳'}"
        elif adf_stationary and kpss_stationary:
            return "两种检验均表明序列是平稳的"
        elif not adf_stationary and not kpss_stationary:
            return "两种检验均表明序列是非平稳的"
        else:
            return "检验结果不一致，建议进一步分析"
    


def calculate_acf_pacf(data: pd.Series, lags: int = 40) -> Tuple[np.ndarray, np.ndarray]:
    """
    计算自相关函数和偏自相关函数
    
    Args:
        data: 时间序列数据
        lags: 滞后期数
    
    Returns:
        ACF和PACF值的元组
    """
    try:
        acf_values = acf(data.dropna(), nlags=lags, fft=True)
        pacf_values = pacf(data.dropna(), nlags=lags, method='ols')
        return acf_values, pacf_values
    except Exception as e:
        print(f"计算ACF/PACF时出错: {e}")
        return np.array([]), np.array([])
