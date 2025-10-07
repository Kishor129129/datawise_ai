"""
Insights Package
Contains statistical analysis, trend detection, anomaly detection, and insight generation
"""

from insights.statistical_analyzer import statistical_analyzer
from insights.trend_analyzer import trend_analyzer
from insights.anomaly_detector import anomaly_detector
from insights.insight_generator import insight_generator

__all__ = [
    'statistical_analyzer',
    'trend_analyzer',
    'anomaly_detector',
    'insight_generator'
]
