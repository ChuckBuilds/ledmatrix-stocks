"""
Configuration Manager for Stock Ticker Plugin

Handles all configuration loading, validation, and runtime changes
for the stock ticker plugin.
"""

from typing import Dict, Any, Optional
import logging


class StockConfigManager:
    """Manages configuration for the stock ticker plugin."""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """Initialize the configuration manager."""
        self.config = config
        self.logger = logger
        
        # Plugin configuration - config is already the plugin-specific config
        self.plugin_config = config
        
        # Initialize all attributes with defaults
        self._init_attributes()
        
        # Load configuration
        self._load_config()
    
    def _init_attributes(self):
        """Initialize all configuration attributes with default values."""
        # Basic settings
        self.enabled = True
        self.display_duration = 30
        # Base scroll speed in pixels per second (used when scroll_speed is a multiplier)
        self.base_scroll_speed = 30.0  # pixels per second
        self.scroll_speed_multiplier = 1.0  # Multiplier from config
        self.scroll_speed = 30.0  # Calculated pixels per second
        self.scroll_delay = 0.001
        self.enable_scrolling = True
        self.toggle_chart = False
        self.dynamic_duration = True
        self.min_duration = 30
        self.max_duration = 300
        self.font_size = 10
        self.update_interval = 300
        
        # Display settings
        self.text_color = [255, 255, 255]
        self.positive_color = [0, 255, 0]
        self.negative_color = [255, 0, 0]
        self.crypto_text_color = [255, 255, 0]
        self.crypto_positive_color = [0, 255, 0]
        self.crypto_negative_color = [255, 0, 0]
        self.stock_symbols = []
        self.crypto_symbols = []
        
        # API configuration
        self.api_config = {}
        self.timeout = 10
        self.retry_count = 3
        self.rate_limit_delay = 0.1
    
    def _load_config(self) -> None:
        """Load and validate configuration."""
        try:
            # Basic settings
            self.enabled = self.plugin_config.get('enabled', True)
            self.display_duration = self.plugin_config.get('display_duration', 30)
            # Load scroll_speed as multiplier (0.5-5.0) and convert to pixels per second
            self.base_scroll_speed = 30.0  # Base speed in pixels per second
            self.scroll_speed_multiplier = self.plugin_config.get('scroll_speed', 1.0)
            # Convert multiplier to pixels per second: base * multiplier
            # Clamp multiplier to valid range (0.5-5.0) per schema
            self.scroll_speed_multiplier = max(0.5, min(5.0, self.scroll_speed_multiplier))
            self.scroll_speed = self.base_scroll_speed * self.scroll_speed_multiplier
            self.scroll_delay = self.plugin_config.get('scroll_delay', 0.001)
            self.enable_scrolling = self.plugin_config.get('enable_scrolling', True)
            self.toggle_chart = self.plugin_config.get('toggle_chart', False)
            self.dynamic_duration = self.plugin_config.get('dynamic_duration', True)
            self.min_duration = self.plugin_config.get('min_duration', 30)
            self.max_duration = self.plugin_config.get('max_duration', 300)
            self.font_size = self.plugin_config.get('font_size', 10)
            self.update_interval = self.plugin_config.get('update_interval', 300)
            
            # Display settings
            self.text_color = self.plugin_config.get('text_color', [255, 255, 255])
            self.positive_color = self.plugin_config.get('positive_color', [0, 255, 0])
            self.negative_color = self.plugin_config.get('negative_color', [255, 0, 0])
            self.crypto_text_color = self.plugin_config.get('crypto_text_color', [255, 255, 0])
            self.crypto_positive_color = self.plugin_config.get('crypto_positive_color', [0, 255, 0])
            self.crypto_negative_color = self.plugin_config.get('crypto_negative_color', [255, 0, 0])
            
            # Stock and crypto symbols
            self.stock_symbols = self.plugin_config.get('stocks', {}).get('stock_symbols', [])
            self.crypto_symbols = self.plugin_config.get('crypto', {}).get('crypto_symbols', [])
            
            
            # API configuration
            self.api_config = self.plugin_config.get('api', {})
            self.timeout = self.api_config.get('timeout', 10)
            self.retry_count = self.api_config.get('retry_count', 3)
            self.rate_limit_delay = self.api_config.get('rate_limit_delay', 0.1)
            
            self.logger.debug("Configuration loaded successfully")
            
        except Exception as e:
            self.logger.error("Error loading configuration: %s", e)
            # Set defaults
            self._set_defaults()
    
    def _set_defaults(self) -> None:
        """Set default configuration values."""
        self.enabled = True
        self.display_duration = 30
        self.base_scroll_speed = 30.0
        self.scroll_speed_multiplier = 1.0
        self.scroll_speed = 30.0  # pixels per second
        self.scroll_delay = 0.001
        self.enable_scrolling = True
        self.toggle_chart = False
        self.dynamic_duration = True
        self.min_duration = 30
        self.max_duration = 300
        self.font_size = 10
        self.update_interval = 300
        self.text_color = [255, 255, 255]
        self.positive_color = [0, 255, 0]
        self.negative_color = [255, 0, 0]
        self.crypto_text_color = [255, 255, 0]
        self.crypto_positive_color = [0, 255, 0]
        self.crypto_negative_color = [255, 0, 0]
        self.stock_symbols = []
        self.crypto_symbols = []
        self.api_config = {}
        self.timeout = 10
        self.retry_count = 3
        self.rate_limit_delay = 0.1
    
    def reload_config(self) -> None:
        """Reload configuration from the main config file."""
        try:
            # This would typically reload from the main config file
            # For now, we'll just reload the current config
            self._load_config()
            self.logger.info("Configuration reloaded successfully")
        except Exception as e:
            self.logger.error("Error reloading configuration: %s", e)
    
    def get_display_duration(self) -> float:
        """Get the display duration in seconds."""
        return float(self.display_duration)
    
    def get_dynamic_duration(self) -> int:
        """Get the dynamic duration setting."""
        return int(self.min_duration) if self.dynamic_duration else int(self.display_duration)
    
    def set_toggle_chart(self, enabled: bool) -> None:
        """Set whether to show mini charts."""
        self.toggle_chart = enabled
        self.logger.debug("Chart toggle set to: %s", enabled)
    
    def set_scroll_speed(self, speed: float) -> None:
        """Set the scroll speed (as multiplier from config, 0.5-5.0)."""
        # Clamp multiplier to valid range per schema
        self.scroll_speed_multiplier = max(0.5, min(5.0, speed))
        # Convert to pixels per second
        self.scroll_speed = self.base_scroll_speed * self.scroll_speed_multiplier
        self.logger.debug("Scroll speed multiplier set to: %.2f (pixels/sec: %.1f)", 
                         self.scroll_speed_multiplier, self.scroll_speed)
    
    def set_scroll_delay(self, delay: float) -> None:
        """Set the scroll delay."""
        self.scroll_delay = max(0.001, min(1.0, delay))
        self.logger.debug("Scroll delay set to: %.3f", self.scroll_delay)
    
    def set_enable_scrolling(self, enabled: bool) -> None:
        """Set whether scrolling is enabled."""
        self.enable_scrolling = enabled
        self.logger.debug("Scrolling enabled: %s", enabled)
    
    def get_plugin_info(self) -> Dict[str, Any]:
        """Get plugin information for display."""
        return {
            'name': 'Stock Ticker Plugin',
            'version': '2.0.0',
            'enabled': self.enabled,
            'scrolling': self.enable_scrolling,
            'chart_enabled': self.toggle_chart,
            'stocks_count': len(self.stock_symbols),
            'crypto_count': len(self.crypto_symbols),
            'scroll_speed': self.scroll_speed_multiplier,  # Return multiplier for config compatibility
            'scroll_speed_px_per_sec': self.scroll_speed,  # Actual pixels per second
            'display_duration': self.display_duration
        }
    
    def validate_config(self) -> bool:
        """Validate the current configuration."""
        try:
            # Check required fields
            if not isinstance(self.stock_symbols, list):
                self.logger.error("Stock symbols must be a list")
                return False
            
            if not isinstance(self.crypto_symbols, list):
                self.logger.error("Crypto symbols must be a list")
                return False
            
            # Check numeric values
            if not isinstance(self.scroll_speed, (int, float)) or self.scroll_speed <= 0:
                self.logger.error("Scroll speed must be a positive number")
                return False
            
            if not isinstance(self.display_duration, (int, float)) or self.display_duration <= 0:
                self.logger.error("Display duration must be a positive number")
                return False
            
            # Check color values
            for color_name in ['text_color', 'positive_color', 'negative_color', 
                             'crypto_text_color', 'crypto_positive_color', 'crypto_negative_color']:
                color = getattr(self, color_name, None)
                if not isinstance(color, list) or len(color) != 3:
                    self.logger.error("%s must be a list of 3 integers (RGB)", color_name)
                    return False
                
                for component in color:
                    if not isinstance(component, int) or not (0 <= component <= 255):
                        self.logger.error("%s components must be integers between 0 and 255", color_name)
                        return False
            
            self.logger.debug("Configuration validation passed")
            return True
            
        except Exception as e:
            self.logger.error("Error validating configuration: %s", e)
            return False
