"""
In-memory geolocation service using ip-to-country library.
Fast, lightweight, and completely free IP geolocation.
"""
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class IPToCountryService:
    """Service for IP geolocation using ip-to-country library."""
    
    def __init__(self):
        try:
            import ip_to_country
            self.ip_to_country = ip_to_country.IpToCountry()
            logger.info("ip-to-country library initialized successfully")
        except ImportError:
            logger.error("ip-to-country library not found. Please install with: pip install ip-to-country")
            self.ip_to_country = None
        except Exception as e:
            logger.error("Failed to initialize ip-to-country: %s", e)
            self.ip_to_country = None
    
    def get_location_from_ip(self, ip_address: str) -> Dict[str, str]:
        """
        Get country and city from IP address using ip-to-country library.
        
        Args:
            ip_address: IP address to geolocate
            
        Returns:
            Dict with 'country' and 'city' keys
        """
        try:
            # Skip private/local IPs
            if self._is_private_ip(ip_address):
                return {'country': 'Local', 'city': 'Local'}
            
            # Use ip-to-country library
            if self.ip_to_country:
                country_data = self.ip_to_country.ip_to_country(ip_address)
                if country_data and isinstance(country_data, dict):
                    # Extract country name from the detailed data
                    country_name = country_data.get('country_name', 'Unknown')
                    return {
                        'country': country_name,
                        'city': 'Unknown'  # ip-to-country doesn't provide city data
                    }
            
            # Fallback if library not available
            return {'country': 'Unknown', 'city': 'Unknown'}
            
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
