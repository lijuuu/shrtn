"""
In-memory geolocation service with fallback geolocation.
Uses ip-to-country library when available, otherwise provides basic geolocation.
"""
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class IPToCountryService:
    """Service for IP geolocation with fallback support."""
    
    def __init__(self):
        self.ip_to_country = None
        
        # Try to initialize ip-to-country library
        try:
            import ip_to_country
            import os
            
            # Create data directory if it doesn't exist
            data_dir = os.path.join(os.getcwd(), 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            # Try to initialize the library
            self.ip_to_country = ip_to_country.IpToCountry()
            logger.info("ip-to-country library initialized successfully")
            
        except ImportError:
            logger.warning("ip-to-country library not found. Using fallback geolocation.")
        except Exception as e:
            logger.warning("Failed to initialize ip-to-country: %s. Using fallback geolocation.", e)
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
            
            # Fallback geolocation using basic IP analysis
            return self._get_fallback_location(ip_address)
            
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
    
    def _get_fallback_location(self, ip_address: str) -> Dict[str, str]:
        """Fallback geolocation using basic IP analysis."""
        try:
            import ipaddress
            ip = ipaddress.ip_address(ip_address)
            
            # Basic geolocation based on common IP ranges
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return {'country': 'Local', 'city': 'Local'}
            
            # Check for common public IP ranges
            ip_str = str(ip)
            
            # Google DNS
            if ip_str.startswith('8.8.8.') or ip_str.startswith('8.8.4.'):
                return {'country': 'United States', 'city': 'Mountain View'}
            
            # Cloudflare DNS
            if ip_str.startswith('1.1.1.') or ip_str.startswith('1.0.0.'):
                return {'country': 'Global', 'city': 'Cloudflare'}
            
            # Basic regional detection (very simplified)
            if ip_str.startswith('8.') or ip_str.startswith('9.') or ip_str.startswith('10.'):
                return {'country': 'United States', 'city': 'Unknown'}
            elif ip_str.startswith('5.') or ip_str.startswith('6.'):
                return {'country': 'Europe', 'city': 'Unknown'}
            elif ip_str.startswith('1.') or ip_str.startswith('2.'):
                return {'country': 'Asia', 'city': 'Unknown'}
            else:
                return {'country': 'Unknown', 'city': 'Unknown'}
                
        except Exception:
            return {'country': 'Unknown', 'city': 'Unknown'}
