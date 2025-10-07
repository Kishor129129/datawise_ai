"""
AI-Powered Insight Generator
Generates natural language insights using Gemini AI
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from loguru import logger
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from ai_engine.gemini_handler import gemini_handler
from insights.statistical_analyzer import statistical_analyzer
from insights.trend_analyzer import trend_analyzer
from insights.anomaly_detector import anomaly_detector


class InsightGenerator:
    """
    Generate AI-powered insights from data analysis
    """
    
    def __init__(self):
        """Initialize insight generator"""
        self.gemini = gemini_handler
    
    def generate_comprehensive_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate comprehensive insights for a dataset
        
        Args:
            df: DataFrame to analyze
        
        Returns:
            Dictionary with all insights
        """
        try:
            logger.info("🔍 Generating comprehensive insights...")
            
            # Perform all analyses
            stats = statistical_analyzer.analyze_dataset(df)
            trends = trend_analyzer.analyze_trends(df)
            anomalies = anomaly_detector.detect_anomalies(df)
            patterns = anomaly_detector.detect_unusual_patterns(df)
            
            # Generate AI insights
            ai_insights = self._generate_ai_insights(df, stats, trends, anomalies, patterns)
            
            # Generate key findings
            key_findings = self._extract_key_findings(stats, trends, anomalies)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(stats, trends, anomalies, patterns)
            
            result = {
                'statistics': stats,
                'trends': trends,
                'anomalies': anomalies,
                'patterns': patterns,
                'ai_insights': ai_insights,
                'key_findings': key_findings,
                'recommendations': recommendations
            }
            
            logger.info("✅ Comprehensive insights generated")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error generating comprehensive insights: {e}")
            return {}
    
    def _generate_ai_insights(
        self,
        df: pd.DataFrame,
        stats: Dict[str, Any],
        trends: Dict[str, Any],
        anomalies: Dict[str, Any],
        patterns: List[Dict[str, Any]]
    ) -> str:
        """
        Generate AI-powered natural language insights
        
        Args:
            df: DataFrame
            stats: Statistical analysis results
            trends: Trend analysis results
            anomalies: Anomaly detection results
            patterns: Unusual patterns
        
        Returns:
            Natural language insights
        """
        try:
            # Build context for AI
            context = self._build_analysis_context(df, stats, trends, anomalies, patterns)
            
            # Generate prompt
            prompt = f"""Analyze this dataset and provide 3-5 key insights in natural language.

Dataset Overview:
{context}

Provide insights that are:
1. Actionable and specific
2. Easy to understand for non-technical users
3. Focused on important patterns, trends, or anomalies
4. Presented as bullet points

Format each insight as a single sentence starting with an emoji."""
            
            # Get AI response
            if self.gemini.is_available():
                insights = self.gemini.generate_text(prompt)
                if insights:
                    return insights
            
            # Fallback to rule-based insights
            return self._generate_fallback_insights(stats, trends, anomalies, patterns)
            
        except Exception as e:
            logger.error(f"❌ Error generating AI insights: {e}")
            return self._generate_fallback_insights(stats, trends, anomalies, patterns)
    
    def _build_analysis_context(
        self,
        df: pd.DataFrame,
        stats: Dict[str, Any],
        trends: Dict[str, Any],
        anomalies: Dict[str, Any],
        patterns: List[Dict[str, Any]]
    ) -> str:
        """Build context string for AI analysis"""
        context_parts = []
        
        # Basic stats
        basic = stats.get('basic_stats', {})
        context_parts.append(f"- {basic.get('row_count', 0):,} rows, {basic.get('column_count', 0)} columns")
        context_parts.append(f"- {basic.get('numeric_columns', 0)} numeric, {basic.get('categorical_columns', 0)} categorical columns")
        
        # Data quality
        quality = stats.get('data_quality', {})
        if quality:
            context_parts.append(f"- Data quality score: {quality.get('quality_score', 0):.1f}/100")
        
        # Trends
        increasing_trends = [col for col, t in trends.items() if t.get('trend') == 'increasing']
        decreasing_trends = [col for col, t in trends.items() if t.get('trend') == 'decreasing']
        
        if increasing_trends:
            context_parts.append(f"- Increasing trends: {', '.join(increasing_trends[:3])}")
        if decreasing_trends:
            context_parts.append(f"- Decreasing trends: {', '.join(decreasing_trends[:3])}")
        
        # Anomalies
        total_anomalies = anomalies.get('total_anomalies', 0)
        if total_anomalies > 0:
            context_parts.append(f"- {total_anomalies} anomalies detected")
        
        # Patterns
        if patterns:
            context_parts.append(f"- {len(patterns)} unusual patterns found")
        
        return "\n".join(context_parts)
    
    def _generate_fallback_insights(
        self,
        stats: Dict[str, Any],
        trends: Dict[str, Any],
        anomalies: Dict[str, Any],
        patterns: List[Dict[str, Any]]
    ) -> str:
        """Generate rule-based insights when AI is unavailable"""
        insights = []
        
        # Data quality insight
        quality = stats.get('data_quality', {})
        if quality:
            score = quality.get('quality_score', 0)
            if score >= 90:
                insights.append("✅ Dataset has excellent quality with minimal issues")
            elif score >= 70:
                insights.append("⚠️  Dataset has good quality but some improvements possible")
            else:
                insights.append("🔴 Dataset has quality issues that should be addressed")
        
        # Trend insights
        increasing = [col for col, t in trends.items() if t.get('trend') == 'increasing']
        decreasing = [col for col, t in trends.items() if t.get('trend') == 'decreasing']
        
        if increasing:
            insights.append(f"📈 {len(increasing)} metric(s) showing growth: {', '.join(increasing[:3])}")
        if decreasing:
            insights.append(f"📉 {len(decreasing)} metric(s) declining: {', '.join(decreasing[:3])}")
        
        # Anomaly insights
        total_anomalies = anomalies.get('total_anomalies', 0)
        if total_anomalies > 0:
            insights.append(f"⚠️  Detected {total_anomalies} outliers that may need investigation")
        else:
            insights.append("✅ No significant outliers detected")
        
        # Pattern insights
        if patterns:
            insights.append(f"🔍 Found {len(patterns)} unusual patterns requiring attention")
        
        return "\n".join(insights) if insights else "Dataset appears normal with no significant findings."
    
    def _extract_key_findings(
        self,
        stats: Dict[str, Any],
        trends: Dict[str, Any],
        anomalies: Dict[str, Any]
    ) -> List[str]:
        """Extract key findings from analysis"""
        findings = []
        
        # Most significant trend
        max_change = 0
        max_change_col = None
        for col, trend_data in trends.items():
            change_pct = abs(trend_data.get('change_percentage', 0))
            if change_pct > max_change:
                max_change = change_pct
                max_change_col = col
        
        if max_change_col and max_change > 10:
            trend_type = trends[max_change_col].get('trend')
            findings.append(f"Largest change: {max_change_col} {trend_type} by {max_change:.1f}%")
        
        # Correlations
        corr_analysis = stats.get('correlation_analysis', {})
        strong_corrs = corr_analysis.get('strong_correlations', [])
        if strong_corrs:
            findings.append(f"Found {len(strong_corrs)} strong correlations between variables")
        
        # Outliers
        if anomalies.get('total_anomalies', 0) > 0:
            findings.append(f"Detected outliers in {anomalies.get('affected_columns', 0)} columns")
        
        return findings
    
    def _generate_recommendations(
        self,
        stats: Dict[str, Any],
        trends: Dict[str, Any],
        anomalies: Dict[str, Any],
        patterns: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Data quality recommendations
        quality = stats.get('data_quality', {})
        if quality:
            recommendations.extend(quality.get('recommendations', []))
        
        # Trend recommendations
        decreasing = [col for col, t in trends.items() if t.get('trend') == 'decreasing']
        if len(decreasing) > 0:
            recommendations.append(f"Investigate declining trends in: {', '.join(decreasing[:3])}")
        
        # Anomaly recommendations
        if anomalies.get('total_anomalies', 0) > 10:
            recommendations.append("Review and validate outliers - they may indicate data quality issues or exceptional cases")
        
        # Pattern recommendations
        for pattern in patterns[:3]:
            if pattern['type'] == 'sudden_spike':
                recommendations.append(f"Investigate sudden spikes in {pattern['column']}")
        
        return recommendations


# Global instance
insight_generator = InsightGenerator()

