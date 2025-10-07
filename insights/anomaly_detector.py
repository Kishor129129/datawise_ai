"""
Anomaly Detector
Detects unusual patterns and outliers in data
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from loguru import logger
import sys
from pathlib import Path
from scipy import stats

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))


class AnomalyDetector:
    """
    Detect anomalies and outliers in data
    """
    
    def __init__(self):
        """Initialize anomaly detector"""
        self.z_threshold = 3  # Z-score threshold
        self.iqr_multiplier = 1.5  # IQR multiplier
    
    def detect_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect anomalies in all numeric columns
        
        Args:
            df: DataFrame to analyze
        
        Returns:
            Dictionary with anomaly detection results
        """
        try:
            numeric_cols = df.select_dtypes(include=['number']).columns
            anomalies = {}
            
            for col in numeric_cols:
                anomalies[col] = self.detect_column_anomalies(df, col)
            
            # Overall summary
            total_anomalies = sum(a['count'] for a in anomalies.values())
            
            logger.info(f"✅ Detected {total_anomalies} anomalies across {len(anomalies)} columns")
            
            return {
                'column_anomalies': anomalies,
                'total_anomalies': total_anomalies,
                'affected_columns': len([a for a in anomalies.values() if a['count'] > 0])
            }
            
        except Exception as e:
            logger.error(f"❌ Error detecting anomalies: {e}")
            return {}
    
    def detect_column_anomalies(self, df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """
        Detect anomalies in a specific column
        
        Args:
            df: DataFrame
            column: Column name
        
        Returns:
            Dictionary with anomaly information
        """
        try:
            data = df[column].dropna()
            
            if len(data) < 4:
                return {'count': 0, 'method': 'insufficient_data'}
            
            # Use IQR method for outlier detection
            q1 = data.quantile(0.25)
            q3 = data.quantile(0.75)
            iqr = q3 - q1
            
            lower_bound = q1 - self.iqr_multiplier * iqr
            upper_bound = q3 + self.iqr_multiplier * iqr
            
            # Detect outliers
            outliers = data[(data < lower_bound) | (data > upper_bound)]
            outlier_indices = outliers.index.tolist()
            
            # Calculate Z-scores for validation
            z_scores = np.abs(stats.zscore(data))
            z_outliers = data[z_scores > self.z_threshold]
            
            return {
                'count': len(outliers),
                'percentage': float((len(outliers) / len(data)) * 100),
                'method': 'IQR',
                'lower_bound': float(lower_bound),
                'upper_bound': float(upper_bound),
                'outlier_values': outliers.tolist()[:10],  # First 10
                'outlier_indices': outlier_indices[:10],
                'z_score_outliers': len(z_outliers),
                'severity': self._assess_severity(len(outliers), len(data))
            }
            
        except Exception as e:
            logger.error(f"❌ Error detecting column anomalies: {e}")
            return {'count': 0, 'method': 'error'}
    
    def detect_unusual_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detect unusual patterns in the dataset
        
        Args:
            df: DataFrame to analyze
        
        Returns:
            List of unusual patterns found
        """
        patterns = []
        
        try:
            # Check for sudden spikes
            numeric_cols = df.select_dtypes(include=['number']).columns
            
            for col in numeric_cols:
                data = df[col].dropna()
                
                if len(data) < 3:
                    continue
                
                # Check for sudden changes
                diffs = data.diff().abs()
                mean_diff = diffs.mean()
                std_diff = diffs.std()
                
                if std_diff > 0:
                    spike_threshold = mean_diff + 3 * std_diff
                    spikes = diffs[diffs > spike_threshold]
                    
                    if len(spikes) > 0:
                        patterns.append({
                            'type': 'sudden_spike',
                            'column': col,
                            'count': len(spikes),
                            'description': f"Detected {len(spikes)} sudden spikes in {col}"
                        })
            
            # Check for constant values in supposedly variable data
            for col in numeric_cols:
                unique_ratio = df[col].nunique() / len(df)
                if unique_ratio < 0.01 and len(df) > 100:
                    patterns.append({
                        'type': 'low_variance',
                        'column': col,
                        'unique_ratio': float(unique_ratio),
                        'description': f"{col} has very low variance (only {df[col].nunique()} unique values)"
                    })
            
            # Check for suspicious distributions
            for col in numeric_cols:
                data = df[col].dropna()
                
                if len(data) > 30:
                    skewness = data.skew()
                    if abs(skewness) > 2:
                        patterns.append({
                            'type': 'skewed_distribution',
                            'column': col,
                            'skewness': float(skewness),
                            'description': f"{col} is highly skewed (skewness: {skewness:.2f})"
                        })
            
            return patterns
            
        except Exception as e:
            logger.error(f"❌ Error detecting unusual patterns: {e}")
            return []
    
    def _assess_severity(self, outlier_count: int, total_count: int) -> str:
        """
        Assess severity of outliers
        
        Args:
            outlier_count: Number of outliers
            total_count: Total number of data points
        
        Returns:
            Severity level
        """
        percentage = (outlier_count / total_count) * 100
        
        if percentage > 10:
            return 'critical'
        elif percentage > 5:
            return 'high'
        elif percentage > 2:
            return 'moderate'
        else:
            return 'low'
    
    def generate_anomaly_report(self, anomalies: Dict[str, Any]) -> str:
        """
        Generate a human-readable anomaly report
        
        Args:
            anomalies: Anomaly detection results
        
        Returns:
            Report text
        """
        try:
            if anomalies.get('total_anomalies', 0) == 0:
                return "✅ No significant anomalies detected in the dataset."
            
            report_parts = []
            report_parts.append(f"⚠️  Detected {anomalies['total_anomalies']} anomalies across {anomalies['affected_columns']} columns.")
            
            # Detail by column
            for col, data in anomalies.get('column_anomalies', {}).items():
                if data['count'] > 0:
                    severity = data.get('severity', 'unknown')
                    report_parts.append(f"  - {col}: {data['count']} outliers ({severity} severity)")
            
            return "\n".join(report_parts)
            
        except Exception as e:
            logger.error(f"❌ Error generating anomaly report: {e}")
            return "Unable to generate anomaly report."


# Global instance
anomaly_detector = AnomalyDetector()

