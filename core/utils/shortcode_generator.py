"""
Shortcode generation utilities.
"""
import logging
import random
import string
from typing import Optional
from core.dependencies.service_registry import service_registry

logger = logging.getLogger(__name__)


class ShortcodeGenerator:
    """Generates unique shortcodes for URLs."""
    
    # Character sets for different shortcode types
    ALPHANUMERIC = string.ascii_letters + string.digits
    ALPHANUMERIC_LOWER = string.ascii_lowercase + string.digits
    ALPHANUMERIC_UPPER = string.ascii_uppercase + string.digits
    ALPHANUMERIC_MIXED = string.ascii_letters + string.digits
    WITH_SYMBOLS = string.ascii_letters + string.digits + '-_'
    
    def __init__(self, length: int = 6, charset: str = None):
        self.length = length
        self.charset = charset or self.ALPHANUMERIC_LOWER
    
    def generate_random(self) -> str:
        """Generate a random shortcode."""
        return ''.join(random.choices(self.charset, k=self.length))
    
    def generate_from_url(self, url: str) -> str:
        """Generate shortcode based on URL content."""
        # Extract meaningful parts from URL
        import re
        
        # Remove protocol and common words
        clean_url = re.sub(r'^https?://', '', url)
        clean_url = re.sub(r'www\.', '', clean_url)
        
        # Extract domain and path parts
        parts = clean_url.split('/')
        domain = parts[0].split('.')[0] if parts else 'url'
        
        # Create shortcode from domain
        shortcode = re.sub(r'[^a-zA-Z0-9]', '', domain)[:4]
        
        # Add random suffix if too short
        if len(shortcode) < 3:
            shortcode += ''.join(random.choices(self.charset, k=3))
        
        # Ensure minimum length
        while len(shortcode) < self.length:
            shortcode += random.choice(self.charset)
        
        return shortcode[:self.length]
    
    def generate_sequential(self, counter: int) -> str:
        """Generate sequential shortcode based on counter."""
        # Convert counter to base36 for shorter representation
        import math
        
        if counter == 0:
            return 'a' * self.length
        
        # Use base36 encoding
        chars = string.ascii_lowercase + string.digits
        result = ''
        
        while counter > 0:
            result = chars[counter % 36] + result
            counter //= 36
        
        # Pad with 'a' if too short
        while len(result) < self.length:
            result = 'a' + result
        
        return result[:self.length]
    
    def generate_memorable(self) -> str:
        """Generate memorable shortcode using word patterns."""
        # Simple word patterns for memorability
        patterns = [
            lambda: f"{random.choice(['pro', 'max', 'ultra', 'mega'])}{random.randint(10, 99)}",
            lambda: f"{random.choice(['fast', 'quick', 'rapid', 'swift'])}{random.choice(['ly', 'er', 'est'])}",
            lambda: f"{random.choice(['link', 'url', 'web', 'net'])}{random.randint(100, 999)}",
            lambda: f"{random.choice(['go', 'to', 'me', 'us'])}{random.choice(['link', 'url', 'web'])}",
        ]
        
        pattern = random.choice(patterns)
        return pattern()[:self.length]
    
    def is_valid_shortcode(self, shortcode: str) -> bool:
        """Validate shortcode format."""
        if not shortcode or len(shortcode) < 3:
            return False
        
        if len(shortcode) > 50:
            return False
        
        # Check if contains only allowed characters
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', shortcode):
            return False
        
        # Cannot start or end with hyphen or underscore
        if shortcode.startswith(('-', '_')) or shortcode.endswith(('-', '_')):
            return False
        
        # Reserved shortcodes
        reserved = ['admin', 'api', 'www', 'mail', 'ftp', 'root', 'system', 'test', 'dev', 'staging', 'prod', 'null', 'undefined']
        if shortcode.lower() in reserved:
            return False
        
        return True
    
    def is_shortcode_available(self, namespace_id: int, shortcode: str) -> bool:
        """Check if shortcode is available in namespace."""
        try:
            from core.dependencies.service_registry import service_registry
            url_service = service_registry.get_url_service()
            
            # Check if shortcode exists in namespace
            existing_url = url_service.get_by_id((namespace_id, shortcode))
            return existing_url is None
            
        except Exception as e:
            logger.error("Failed to check shortcode availability: %s", e)
            return False
    
    def generate_unique_shortcode(self, namespace_id: int, method: str = 'random', custom_shortcode: str = None) -> str:
        """Generate a unique shortcode for the given namespace."""
        
        # If custom shortcode provided, validate and check availability
        if custom_shortcode:
            if not self.is_valid_shortcode(custom_shortcode):
                raise ValueError(f"Invalid shortcode format: {custom_shortcode}")
            
            if not self.is_shortcode_available(namespace_id, custom_shortcode):
                raise ValueError(f"Shortcode '{custom_shortcode}' is already taken in this namespace")
            
            return custom_shortcode
        
        # Generate shortcode based on method
        max_attempts = 100
        attempts = 0
        
        while attempts < max_attempts:
            if method == 'random':
                shortcode = self.generate_random()
            elif method == 'url_based':
                # This would need the original URL, so fallback to random
                shortcode = self.generate_random()
            elif method == 'sequential':
                shortcode = self.generate_sequential(attempts)
            elif method == 'memorable':
                shortcode = self.generate_memorable()
            else:
                shortcode = self.generate_random()
            
            # Check if available
            if self.is_shortcode_available(namespace_id, shortcode):
                return shortcode
            
            attempts += 1
        
        # If we couldn't generate a unique shortcode, raise error
        raise ValueError(f"Could not generate unique shortcode after {max_attempts} attempts")
