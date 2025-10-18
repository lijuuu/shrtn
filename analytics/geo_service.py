"""
In-memory geolocation service for IP address to country/city mapping.
Uses local MaxMind GeoIP2 database for fast, offline geolocation.
"""
import logging
import os
from typing import Dict, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

class GeoLocationService:
    """Service for IP geolocation using local MaxMind database."""
    
    def __init__(self):
        self.db_path = getattr(settings, 'GEOIP_DATABASE_PATH', None)
        self.reader = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the MaxMind GeoIP2 database reader."""
        try:
            if not self.db_path or not os.path.exists(self.db_path):
                logger.warning("GeoIP database not found at %s. Using fallback geolocation.", self.db_path)
                return
            
            import geoip2.database
            self.reader = geoip2.database.Reader(self.db_path)
            logger.info("GeoIP database initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize GeoIP database: %s", e)
            self.reader = None
    
    def get_location_from_ip(self, ip_address: str) -> Dict[str, str]:
        """
        Get country and city from IP address using local database.
        
        Args:
            ip_address: IP address to geolocate
            
        Returns:
            Dict with 'country' and 'city' keys
        """
        try:
            # Skip private/local IPs
            if self._is_private_ip(ip_address):
                return {'country': 'Local', 'city': 'Local'}
            
            # Try local database first
            if self.reader:
                location = self._get_local_location(ip_address)
                if location:
                    return location
            
            # Fallback to basic IP analysis
            return self._get_basic_location(ip_address)
            
        except Exception as e:
            logger.error("Failed to get location for IP %s: %s", ip_address, e)
            return {'country': 'Unknown', 'city': 'Unknown'}
    
    def _is_private_ip(self, ip_address: str) -> bool:
        """Check if IP is private/local."""
        try:
            import ipaddress
            ip = ipaddress.ip_address(ip_address)
            return ip.is_private or ip.is_loopback or ip.is_link_local
        except:
            return True
    
    def _get_local_location(self, ip_address: str) -> Optional[Dict[str, str]]:
        """Get location using local MaxMind database."""
        try:
            response = self.reader.city(ip_address)
            
            country = response.country.name or 'Unknown'
            city = response.city.name or 'Unknown'
            
            return {
                'country': country,
                'city': city
            }
            
        except Exception as e:
            logger.debug("Local database lookup failed for IP %s: %s", ip_address, e)
            return None
    
    def _get_basic_location(self, ip_address: str) -> Dict[str, str]:
        """Basic IP analysis for common IP ranges."""
        try:
            import ipaddress
            ip = ipaddress.ip_address(ip_address)
            
            # Common IP ranges for major countries (simplified)
            if self._is_us_ip(ip):
                return {'country': 'United States', 'city': 'Unknown'}
            elif self._is_eu_ip(ip):
                return {'country': 'Europe', 'city': 'Unknown'}
            elif self._is_asia_ip(ip):
                return {'country': 'Asia', 'city': 'Unknown'}
            else:
                return {'country': 'Unknown', 'city': 'Unknown'}
                
        except Exception:
            return {'country': 'Unknown', 'city': 'Unknown'}
    
    def _is_us_ip(self, ip) -> bool:
        """Check if IP is likely from US (simplified)."""
        # This is a very basic check - in production you'd want more sophisticated analysis
        return False  # Simplified for now
    
    def _is_eu_ip(self, ip) -> bool:
        """Check if IP is likely from EU (simplified)."""
        return False  # Simplified for now
    
    def _is_asia_ip(self, ip) -> bool:
        """Check if IP is likely from Asia (simplified)."""
        return False  # Simplified for now
    
    def close(self):
        """Close the database reader."""
        if self.reader:
            self.reader.close()
            self.reader = None
