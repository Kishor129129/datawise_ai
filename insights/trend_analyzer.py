"""
Trend Analyzer
Detects and analyzes trends in time series and sequential data
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))


class TrendAnalyzer:
    """
    Analyze trends in data
    """
    
    def __init__(self):
        """Initialize trend analyzer"""
        pass
    
    def analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze trends in all numeric columns
        
        Args:
            df: DataFrame to analyze
        
        Returns:
            Dictionary with trend analysis
        """
        try:
            numeric_cols = df.select_dtypes(include=['number']).columns
            trends = {}
            
            for col in numeric_cols:
                trends[col] = self.analyze_column_trend(df, col)
            
            logger.info(f"✅ Analyzed trends for {len(trends)} columns")
            return trends
            
        except Exception as e:
            logger.error(f"❌ Error analyzing trends: {e}")
            return {}
    
    def analyze_column_trend(self, df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """
        Analyze trend for a specific column
        
        Args:
            df: DataFrame
            column: Column name
        
        Returns:
            Dictionary with trend information
        """
        try:
            data = df[column].dropna()
            
            if len(data) < 2:
                return {'trend': 'insufficient_data'}
            
            # Calculate trend direction
            first_half_mean = data.iloc[:len(data)//2].mean()
            second_half_mean = data.iloc[len(data)//2:].mean()
            
            change = second_half_mean - first_half_mean
            change_percentage = (change / first_half_mean * 100) if first_half_mean != 0 else 0
            
            # Determine trend type
            if abs(change_percentage) < 5:
                trend_type = 'stable'
            elif change_percentage > 0:
                trend_type = 'increasing'
            else:
                trend_type = 'decreasing'
            
            # Calculate rate of change
            if len(data) > 1:
                rate_of_change = (data.iloc[-1] - data.iloc[0]) / len(data)
            else:
                rate_of_change = 0
            
            # Detect volatility
            volatility = float(data.std() / data.mean() * 100) if data.mean() != 0 else 0
            
            return {
                'trend': trend_type,
                'change': float(change),
                'change_percentage': float(change_percentage),
                'rate_of_change': float(rate_of_change),
                'volatility': volatility,
                'first_value': float(data.iloc[0]),
                'last_value': float(data.iloc[-1]),
                'min_value': float(data.min()),
                'max_value': float(data.max()),
                'mean_value': float(data.mean())
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing column trend: {e}")
            return {'trend': 'error'}
    
    def detect_seasonality(self, data: pd.Series, period: int = 7) -> Dict[str, Any]:
        """
        Detect seasonality patterns
        
        Args:
            data: Time series data
            period: Expected period length
        
        Returns:
            Dictionary with seasonality information
        """
        try:
            if len(data) < period * 2:
                return {'has_seasonality': False, 'reason': 'insufficient_data'}
            
            # Simple seasonality detection using autocorrelation
            autocorr = data.autocorr(lag=period)
            
            has_seasonality = autocorr > 0.5
            
            return {
                'has_seasonality': bool(has_seasonality),
                'autocorrelation': float(autocorr),
                'period': period,
                'confidence': 'high' if autocorr > 0.7 else 'moderate' if autocorr > 0.5 else 'low'
            }
            
        except Exception as e:
            logger.error(f"❌ Error detecting seasonality: {e}")
            return {'has_seasonality': False, 'reason': 'error'}
    
    def calculate_moving_average(self, data: pd.Series, window: int = 5) -> pd.Series:
        """
        Calculate moving average
        
        Args:
            data: Series to smooth
            window: Window size
        
        Returns:
            Moving average series
        """
        try:
            return data.rolling(window=window, min_periods=1).mean()
        except Exception as e:
            logger.error(f"❌ Error calculating moving average: {e}")
            return data
    
    def identify_turning_points(self, data: pd.Series) -> Dict[str, Any]:
        """
        Identify peaks and valleys in data
        
        Args:
            data: Series to analyze
        
        Returns:
            Dictionary with turning points
        """
        try:
            if len(data) < 3:
                return {'peaks': [], 'valleys': []}
            
            # Find local maxima (peaks)
            peaks = []
            for i in range(1, len(data) - 1):
                if data.iloc[i] > data.iloc[i-1] and data.iloc[i] > data.iloc[i+1]:
                    peaks.append({'index': i, 'value': float(data.iloc[i])})
            
            # Find local minima (valleys)
            valleys = []
            for i in range(1, len(data) - 1):
                if data.iloc[i] < data.iloc[i-1] and data.iloc[i] < data.iloc[i+1]:
                    valleys.append({'index': i, 'value': float(data.iloc[i])})
            
            return {
                'peaks': peaks[:10],  # First 10 peaks
                'valleys': valleys[:10],  # First 10 valleys
                'peak_count': len(peaks),
                'valley_count': len(valleys)
            }
            
        except Exception as e:
            logger.error(f"❌ Error identifying turning points: {e}")
            return {'peaks': [], 'valleys': []}
    
    def generate_trend_summary(self, trends: Dict[str, Any]) -> List[str]:
        """
        Generate human-readable trend summaries
        
        Args:
            trends: Dictionary with trend analysis
        
        Returns:
            List of summary statements
        """
        summaries = []
        
        try:
            for column, trend_data in trends.items():
                if trend_data.get('trend') == 'increasing':
                    change_pct = trend_data.get('change_percentage', 0)
                    summaries.append(f"📈 {column} is increasing by {abs(change_pct):.1f}%")
                elif trend_data.get('trend') == 'decreasing':
                    change_pct = trend_data.get('change_percentage', 0)
                    summaries.append(f"📉 {column} is decreasing by {abs(change_pct):.1f}%")
                elif trend_data.get('trend') == 'stable':
                    summaries.append(f"➡️  {column} remains stable")
            
            return summaries
            
        except Exception as e:
            logger.error(f"❌ Error generating trend summary: {e}")
            return []


# Global instance
trend_analyzer = TrendAnalyzer()

