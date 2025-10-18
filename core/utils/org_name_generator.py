"""
Organization name generator for creating unique organization names.
"""
import random
import string
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class OrganizationNameGenerator:
    """
    Generates unique organization names with various patterns.
    """
    
    # Organization name patterns
    PATTERNS = [
        "{adjective} {noun} {suffix}",
        "{noun} {adjective} {suffix}",
        "{adjective} {noun}",
        "{noun} {suffix}",
        "{adjective} {noun} {number}",
        "{noun} {number}",
    ]
    
    # Word lists
    ADJECTIVES = [
        "Swift", "Bright", "Dynamic", "Creative", "Innovative", "Agile", "Smart",
        "Rapid", "Efficient", "Modern", "Advanced", "Premium", "Elite", "Prime",
        "Ultimate", "Superior", "Excellent", "Outstanding", "Remarkable", "Exceptional",
        "Powerful", "Strong", "Robust", "Reliable", "Secure", "Trusted", "Proven",
        "Expert", "Professional", "Skilled", "Talented", "Gifted", "Brilliant"
    ]
    
    NOUNS = [
        "Solutions", "Systems", "Technologies", "Innovations", "Ventures", "Enterprises",
        "Corporations", "Companies", "Organizations", "Groups", "Teams", "Collectives",
        "Networks", "Alliances", "Partnerships", "Collaborations", "Associations",
        "Foundations", "Institutes", "Centers", "Hubs", "Labs", "Studios", "Workshops",
        "Studios", "Agencies", "Services", "Consulting", "Advisory", "Management",
        "Development", "Research", "Design", "Creative", "Digital", "Tech", "Data",
        "Cloud", "AI", "Machine", "Learning", "Analytics", "Intelligence", "Smart"
    ]
    
    SUFFIXES = [
        "Ltd", "LLC", "Inc", "Corp", "Group", "Co", "Partners", "Associates",
        "Consulting", "Services", "Solutions", "Technologies", "Systems",
        "Enterprises", "Ventures", "Holdings", "International", "Global"
    ]
    
    def __init__(self):
        # Lazy load organization service to avoid circular imports
        self._organization_service = None
    
    @property
    def organization_service(self):
        if self._organization_service is None:
            from core.dependencies.service_registry import service_registry
            self._organization_service = service_registry.get_organization_service()
        return self._organization_service
    
    def generate_random_name(self) -> str:
        """Generate a random organization name using patterns."""
        pattern = random.choice(self.PATTERNS)
        
        # Fill in the pattern
        name = pattern.format(
            adjective=random.choice(self.ADJECTIVES),
            noun=random.choice(self.NOUNS),
            suffix=random.choice(self.SUFFIXES),
            number=random.randint(1, 999)
        )
        
        return name
    
    def generate_unique_name(self, max_attempts: int = 10) -> str:
        """Generate a unique organization name."""
        for _ in range(max_attempts):
            name = self.generate_random_name()
            if self.is_name_available(name):
                return name
        
        # If we can't find a unique name, add a random suffix
        base_name = self.generate_random_name()
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        return f"{base_name}_{random_suffix}"
    
    def is_name_available(self, name: str) -> bool:
        """Check if organization name is available."""
        try:
            # Check if name exists in database
            existing_org = self.organization_service.get_by_name(name)
            return existing_org is None
        except Exception as e:
            logger.warning("Failed to check organization name availability: %s", e)
            return True  # Assume available if check fails
    
    def generate_custom_name(self, base_name: str) -> str:
        """Generate a custom organization name based on user input."""
        if not base_name or len(base_name.strip()) < 2:
            return self.generate_unique_name()
        
        base_name = base_name.strip()
        
        # Check if base name is available
        if self.is_name_available(base_name):
            return base_name
        
        # Try variations
        variations = [
            f"{base_name} {random.choice(self.SUFFIXES)}",
            f"{base_name} {random.choice(self.ADJECTIVES)}",
            f"{base_name} {random.randint(1, 999)}",
            f"{base_name}_{random.randint(1, 999)}",
            f"{base_name}_{''.join(random.choices(string.ascii_lowercase, k=3))}",
        ]
        
        for variation in variations:
            if self.is_name_available(variation):
                return variation
        
        # If no variation works, generate completely random name
        return self.generate_unique_name()


def generate_org_name(custom_name: Optional[str] = None) -> str:
    """
    Generate an organization name.
    
    Args:
        custom_name: Optional custom name to use as base
        
    Returns:
        Unique organization name
    """
    generator = OrganizationNameGenerator()
    
    if custom_name:
        return generator.generate_custom_name(custom_name)
    else:
        return generator.generate_unique_name()