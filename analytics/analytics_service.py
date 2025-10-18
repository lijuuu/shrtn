"""
Analytics service for tracking URL clicks and generating reports.
"""
import logging
from datetime import datetime, timezone, date, timedelta
from typing import Dict, Any, Optional, List
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from core.database.scylla import ScyllaDBConnection
from analytics.ip_to_country_service import IPToCountryService

logger = logging.getLogger(__name__)

@dataclass
class ClickAnalytics:
    """Data class for click analytics."""
    namespace_id: int
    shortcode: str
    click_date: date
    click_timestamp: datetime
    user_agent: str
    ip_address: str
    referer: str
    country: str
    city: str

class AnalyticsService:
    """Service for URL analytics and reporting."""
    
    def __init__(self, scylla: ScyllaDBConnection):
        self.scylla = scylla
        self.geo_service = IPToCountryService()
    
    def track_click(
        self,
        namespace_id: int,
        shortcode: str,
        ip_address: str,
        user_agent: str = "",
        referer: str = ""
    ) -> bool:
        """
        Track a URL lookup with country-based analytics.
        
        Args:
            namespace_id: Namespace ID
            shortcode: URL shortcode
            ip_address: User's IP address
            user_agent: User's browser agent
            referer: Referring URL
            
        Returns:
            bool: True if tracking successful
        """
        try:
            # Get geolocation data
            location = self.geo_service.get_location_from_ip(ip_address)
            country = location.get('country', 'Unknown')
            
            # Prepare analytics data
            now = datetime.now(timezone.utc)
            lookup_date = now.date()
            
            # Insert into url_analytics table
            insert_query = """
            INSERT INTO url_analytics (
                namespace_id, shortcode, lookup_date, lookup_timestamp,
                country, ip_address, user_agent, referer
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            self.scylla.execute_update(insert_query, [
                namespace_id, shortcode, lookup_date, now,
                country, ip_address, user_agent or 'Unknown', referer or 'Direct'
            ])
            
            logger.info("Tracked lookup for %s:%s from %s (%s)", 
                       namespace_id, shortcode, ip_address, country)
            
            return True
            
        except Exception as e:
            logger.error("Failed to track lookup: %s", e)
            return False
    
    def get_url_analytics(
        self,
        namespace_id: int,
        shortcode: str,
        days: int = 30,
        time_filter: str = None
    ) -> Dict[str, Any]:
        """
        Get analytics for a specific URL.
        
        Args:
            namespace_id: Namespace ID
            shortcode: URL shortcode
            days: Number of days to analyze
            time_filter: Time filter ('1day', '3days', '7days', '30days')
            
        Returns:
            Dict with analytics data
        """
        try:
            # Calculate date range based on time filter
            end_date = date.today()
            if time_filter == '1day':
                start_date = end_date
                days = 1
            elif time_filter == '3days':
                start_date = end_date - timedelta(days=3)
                days = 3
            elif time_filter == '7days':
                start_date = end_date - timedelta(days=7)
                days = 7
            elif time_filter == '30days':
                start_date = end_date - timedelta(days=30)
                days = 30
            else:
                start_date = end_date - timedelta(days=days)
            
            # Get analytics data
            query = """
            SELECT lookup_date, lookup_timestamp, user_agent, ip_address, 
                   referer, country
            FROM url_analytics
            WHERE namespace_id = ? AND shortcode = ?
            AND lookup_date >= ? AND lookup_date <= ?
            ORDER BY lookup_date DESC, lookup_timestamp DESC
            """
            
            results = self.scylla.execute_query(query, [
                namespace_id, shortcode, start_date, end_date
            ])
            
            # Process analytics data
            analytics = self._process_analytics_data(results)
            
            return {
                'url': f"{namespace_id}:{shortcode}",
                'period_days': days,
                'total_clicks': len(results),
                'analytics': analytics
            }
            
        except Exception as e:
            logger.error("Failed to get URL analytics: %s", e)
            return {'error': str(e)}
    
    def get_namespace_analytics(
        self,
        namespace_id: int,
        days: int = 30,
        time_filter: str = None
    ) -> Dict[str, Any]:
        """
        Get analytics for all URLs in a namespace.
        
        Args:
            namespace_id: Namespace ID
            days: Number of days to analyze
            time_filter: Time filter ('1day', '3days', '7days', '30days')
            
        Returns:
            Dict with namespace analytics
        """
        try:
            # Calculate date range based on time filter
            end_date = date.today()
            if time_filter == '1day':
                start_date = end_date
                days = 1
            elif time_filter == '3days':
                start_date = end_date - timedelta(days=3)
                days = 3
            elif time_filter == '7days':
                start_date = end_date - timedelta(days=7)
                days = 7
            elif time_filter == '30days':
                start_date = end_date - timedelta(days=30)
                days = 30
            else:
                start_date = end_date - timedelta(days=days)
            
            # Get all analytics for namespace
            query = """
            SELECT shortcode, lookup_date, lookup_timestamp, user_agent, 
                   ip_address, referer, country
            FROM url_analytics
            WHERE namespace_id = ?
            AND lookup_date >= ? AND lookup_date <= ?
            ORDER BY lookup_date DESC, lookup_timestamp DESC
            """
            
            results = self.scylla.execute_query(query, [
                namespace_id, start_date, end_date
            ])
            
            # Process analytics data
            analytics = self._process_analytics_data(results)
            
            # Group by URL
            url_analytics = {}
            for result in results:
                shortcode = result.shortcode
                if shortcode not in url_analytics:
                    url_analytics[shortcode] = []
                url_analytics[shortcode].append(result)
            
            # Calculate per-URL stats
            url_stats = {}
            for shortcode, clicks in url_analytics.items():
                url_stats[shortcode] = {
                    'total_clicks': len(clicks),
                    'unique_ips': len(set(click.ip_address for click in clicks)),
                    'countries': list(set(click.country for click in clicks if click.country != 'Unknown')),
                    'top_countries': self._get_top_countries(clicks)
                }
            
            return {
                'namespace_id': namespace_id,
                'period_days': days,
                'total_clicks': len(results),
                'unique_urls': len(url_stats),
                'analytics': analytics,
                'url_stats': url_stats
            }
            
        except Exception as e:
            logger.error("Failed to get namespace analytics: %s", e)
            return {'error': str(e)}
    
    def _process_analytics_data(self, results: List) -> Dict[str, Any]:
        """Process raw analytics data into summary statistics."""
        if not results:
            return {
                'daily_clicks': [],
                'country_distribution': {},
                'referer_distribution': {},
                'top_countries': [],
                'unique_ips': 0,
                'total_clicks': 0
            }
        
        # Daily clicks
        daily_clicks = {}
        for result in results:
            lookup_date = result.lookup_date
            daily_clicks[lookup_date] = daily_clicks.get(lookup_date, 0) + 1
        
        # Country distribution
        country_dist = {}
        for result in results:
            country = result.country or 'Unknown'
            country_dist[country] = country_dist.get(country, 0) + 1
        
        # Referer distribution
        referer_dist = {}
        for result in results:
            referer = result.referer or 'Direct'
            referer_dist[referer] = referer_dist.get(referer, 0) + 1
        
        # Top countries
        top_countries = sorted(
            country_dist.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        # Unique IPs
        unique_ips = len(set(result.ip_address for result in results))
        
        return {
            'daily_clicks': [
                {'date': str(date), 'clicks': clicks} 
                for date, clicks in sorted(daily_clicks.items())
            ],
            'country_distribution': country_dist,
            'referer_distribution': referer_dist,
            'top_countries': [{'country': country, 'clicks': clicks} for country, clicks in top_countries],
            'unique_ips': unique_ips,
            'total_clicks': len(results)
        }
    
    def _get_top_countries(self, clicks: List) -> List[Dict[str, Any]]:
        """Get top countries from click data."""
        country_counts = {}
        for click in clicks:
            country = click.country or 'Unknown'
            country_counts[country] = country_counts.get(country, 0) + 1
        
        return [
            {'country': country, 'clicks': count}
            for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
    
    def get_realtime_stats(self, namespace_id: int) -> Dict[str, Any]:
        """Get real-time statistics for a namespace."""
        try:
            # Get today's analytics
            today = date.today()
            
            query = """
            SELECT shortcode, lookup_timestamp, country
            FROM url_analytics
            WHERE namespace_id = ? AND lookup_date = ?
            ORDER BY lookup_timestamp DESC
            """
            
            results = self.scylla.execute_query(query, [namespace_id, today])
            
            # Process real-time data
            recent_clicks = []
            for result in results:
                recent_clicks.append({
                    'shortcode': result.shortcode,
                    'timestamp': result.lookup_timestamp.isoformat(),
                    'country': result.country
                })
            
            return {
                'namespace_id': namespace_id,
                'date': str(today),
                'total_clicks_today': len(results),
                'recent_clicks': recent_clicks[:20],  # Last 20 clicks
                'unique_countries_today': len(set(r.country for r in results if r.country != 'Unknown'))
            }
            
        except Exception as e:
            logger.error("Failed to get real-time stats: %s", e)
            return {'error': str(e)}
    
    def get_country_analytics_with_tiers(
        self,
        namespace_ids: List[int],
        days: int = 30,
        time_filter: str = None
    ) -> Dict[str, Any]:
        """
        Get country analytics with tier counts for multiple namespaces.
        
        Args:
            namespace_ids: List of namespace IDs
            days: Number of days to analyze
            time_filter: Time filter ('1day', '3days', '7days', '30days')
            
        Returns:
            Dict with country analytics including tier counts
        """
        try:
            # Calculate date range based on time filter
            end_date = date.today()
            if time_filter == '1day':
                start_date = end_date
                days = 1
            elif time_filter == '3days':
                start_date = end_date - timedelta(days=3)
                days = 3
            elif time_filter == '7days':
                start_date = end_date - timedelta(days=7)
                days = 7
            elif time_filter == '30days':
                start_date = end_date - timedelta(days=30)
                days = 30
            else:
                start_date = end_date - timedelta(days=days)
            
            # Build query for multiple namespaces
            namespace_placeholders = ','.join(['?' for _ in namespace_ids])
            query = f"""
            SELECT country, COUNT(*) as click_count
            FROM url_analytics
            WHERE namespace_id IN ({namespace_placeholders})
            AND lookup_date >= ? AND lookup_date <= ?
            GROUP BY country
            ORDER BY click_count DESC
            """
            
            results = self.scylla.execute_query(query, namespace_ids + [start_date, end_date])
            
            # Process results
            country_distribution = {}
            total_clicks = 0
            
            for row in results:
                country = row[0] or 'Unknown'
                clicks = row[1]
                country_distribution[country] = clicks
                total_clicks += clicks
            
            # Calculate tier counts
            tier_counts = self._calculate_tier_counts(country_distribution)
            
            # Get top countries with tier information
            top_countries = []
            for country, clicks in sorted(country_distribution.items(), key=lambda x: x[1], reverse=True):
                tier = self._get_country_tier(clicks, tier_counts)
                top_countries.append({
                    'country': country,
                    'clicks': clicks,
                    'tier': tier,
                    'percentage': round((clicks / total_clicks) * 100, 2) if total_clicks > 0 else 0
                })
            
            return {
                'total_clicks': total_clicks,
                'countries': list(country_distribution.keys()),
                'country_distribution': country_distribution,
                'top_countries': top_countries,
                'tier_counts': tier_counts,
                'period_days': days,
                'time_filter': time_filter,
                'namespaces_analyzed': len(namespace_ids)
            }
            
        except Exception as e:
            logger.error("Failed to get country analytics with tiers: %s", e)
            return {'error': str(e)}
    
    def _calculate_tier_counts(self, country_distribution: Dict[str, int]) -> Dict[str, int]:
        """Calculate tier counts based on click distribution."""
        if not country_distribution:
            return {'tier_1': 0, 'tier_2': 0, 'tier_3': 0, 'tier_4': 0}
        
        clicks = list(country_distribution.values())
        clicks.sort(reverse=True)
        
        total_countries = len(clicks)
        if total_countries == 0:
            return {'tier_1': 0, 'tier_2': 0, 'tier_3': 0, 'tier_4': 0}
        
        # Define tier thresholds
        tier_1_threshold = max(clicks) * 0.5  # Top 50% of max clicks
        tier_2_threshold = max(clicks) * 0.25  # 25% of max clicks
        tier_3_threshold = max(clicks) * 0.1   # 10% of max clicks
        
        tier_counts = {'tier_1': 0, 'tier_2': 0, 'tier_3': 0, 'tier_4': 0}
        
        for click_count in clicks:
            if click_count >= tier_1_threshold:
                tier_counts['tier_1'] += 1
            elif click_count >= tier_2_threshold:
                tier_counts['tier_2'] += 1
            elif click_count >= tier_3_threshold:
                tier_counts['tier_3'] += 1
            else:
                tier_counts['tier_4'] += 1
        
        return tier_counts
    
    def _get_country_tier(self, clicks: int, tier_counts: Dict[str, int]) -> str:
        """Get tier for a specific country based on click count."""
        if clicks == 0:
            return 'tier_4'
        
        # This is a simplified tier calculation
        # In a real implementation, you'd use the actual thresholds
        if clicks >= 1000:
            return 'tier_1'
        elif clicks >= 500:
            return 'tier_2'
        elif clicks >= 100:
            return 'tier_3'
        else:
            return 'tier_4'
