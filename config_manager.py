"""
Configuration Manager for Stock Ticker Plugin

Handles all configuration loading, validation, and runtime changes
for the stock ticker plugin.
"""

from typing import Dict, Any
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
        # Scroll speed in pixels per frame (matching old manager)
        self.scroll_speed = 1.0  # Pixels per frame (default 1)
        self.scroll_delay = 0.02  # Seconds between frames (default 0.02)
        self.enable_scrolling = True
        self.toggle_chart = False
        self.dynamic_duration = True
        self.min_duration = 30
        self.max_duration = 300
        self.duration_buffer = 0.1
        self.update_interval = 600  # Default 600 seconds (10 minutes)
        
        # Display settings for stocks
        self.text_color = [255, 255, 255]
        self.positive_color = [0, 255, 0]
        self.negative_color = [255, 0, 0]
        self.show_change = True
        self.show_percentage = True
        self.show_volume = False
        self.show_market_cap = False
        self.stock_display_format = "{symbol}: ${price} ({change}%)"
        
        # Display settings for crypto (loaded from crypto object)
        self.crypto_text_color = [255, 215, 0]  # Default from schema
        self.crypto_positive_color = [0, 255, 0]
        self.crypto_negative_color = [255, 0, 0]
        self.crypto_show_change = True
        self.crypto_show_percentage = True
        self.crypto_display_format = "{symbol}: ${price} ({change}%)"
        
        self.stock_symbols = []
        self.stocks_enabled = True  # Default to enabled for backward compatibility
        self.crypto_symbols = []
        self.crypto_update_interval = 600
        
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
            self.update_interval = self.plugin_config.get('update_interval', 600)
            
            # Display settings (nested under 'display' object)
            # Support both new format (display.*) and old format (top-level)
            display_config = self.plugin_config.get('display', {})
            if display_config:
                # New format - read from display section
                self.scroll_speed = display_config.get('scroll_speed', 1.0)
                self.scroll_delay = display_config.get('scroll_delay', 0.02)
                self.toggle_chart = display_config.get('toggle_chart', True)
                self.dynamic_duration = display_config.get('dynamic_duration', True)
                self.min_duration = display_config.get('min_duration', 30)
                self.max_duration = display_config.get('max_duration', 300)
                self.duration_buffer = display_config.get('duration_buffer', 0.1)
            else:
                # Old format - check top level for backward compatibility
                self.scroll_speed = self.plugin_config.get('scroll_speed', 1.0)
                self.scroll_delay = self.plugin_config.get('scroll_delay', 0.02)
                self.toggle_chart = self.plugin_config.get('toggle_chart', False)
                self.dynamic_duration = self.plugin_config.get('dynamic_duration', True)
                self.min_duration = self.plugin_config.get('min_duration', 30)
                self.max_duration = self.plugin_config.get('max_duration', 300)
                self.duration_buffer = self.plugin_config.get('duration_buffer', 0.1)
            
            # Clamp scroll_speed to valid range (0.5-5.0) per schema
            self.scroll_speed = max(0.5, min(5.0, self.scroll_speed))
            self.enable_scrolling = self.plugin_config.get('enable_scrolling', True)
            
            # Stock configuration (nested under 'stocks' object)
            # Support both new format (stocks.symbols) and old format (top-level symbols)
            stocks_config = self.plugin_config.get('stocks', {})
            self.stocks_enabled = stocks_config.get('enabled', True)  # Default to True for backward compatibility
            
            if self.stocks_enabled:
                if 'symbols' in stocks_config:
                    # New format
                    self.stock_symbols = stocks_config.get('symbols', ["ASTS", "SCHD", "INTC", "NVDA", "T", "VOO", "SMCI"])
                else:
                    # Old format - check top level for backward compatibility
                    self.stock_symbols = self.plugin_config.get('symbols', ["ASTS", "SCHD", "INTC", "NVDA", "T", "VOO", "SMCI"])
                self.stock_display_format = stocks_config.get('display_format', "{symbol}: ${price} ({change}%)")
            else:
                # Stocks disabled - clear symbols
                self.stock_symbols = []
                self.stock_display_format = "{symbol}: ${price} ({change}%)"
            
            # Crypto configuration (nested under 'crypto' object)
            # Support both new format (crypto.symbols) and old format (crypto.crypto_symbols)
            crypto_config = self.plugin_config.get('crypto', {})
            if crypto_config.get('enabled', False):
                # Support both new format (symbols) and old format (crypto_symbols)
                if 'symbols' in crypto_config:
                    self.crypto_symbols = crypto_config.get('symbols', ["BTC-USD", "ETH-USD"])
                else:
                    # Old format - check for crypto_symbols
                    old_symbols = crypto_config.get('crypto_symbols', ["BTC-USD", "ETH-USD"])
                    # Convert old format (BTC) to new format (BTC-USD) if needed
                    self.crypto_symbols = [s if '-USD' in s else f"{s}-USD" for s in old_symbols]
                self.crypto_display_format = crypto_config.get('display_format', "{symbol}: ${price} ({change}%)")
                self.crypto_update_interval = crypto_config.get('update_interval', self.update_interval)
            else:
                self.crypto_symbols = []
                self.crypto_display_format = "{symbol}: ${price} ({change}%)"
                self.crypto_update_interval = self.update_interval
            
            # Customization settings (nested under 'customization' object)
            # Support both new format (customization.stocks.*) and old format (top-level colors)
            customization = self.plugin_config.get('customization', {})
            
            # Stock customization - check new format first, then old format
            stocks_custom = customization.get('stocks', {})
            if stocks_custom:
                self.text_color = [int(float(c)) for c in stocks_custom.get('text_color', [255, 255, 255])]
                self.positive_color = [int(float(c)) for c in stocks_custom.get('positive_color', [0, 255, 0])]
                self.negative_color = [int(float(c)) for c in stocks_custom.get('negative_color', [255, 0, 0])]
            else:
                # Old format - check top level for backward compatibility
                self.text_color = [int(float(c)) for c in self.plugin_config.get('text_color', [255, 255, 255])]
                self.positive_color = [int(float(c)) for c in self.plugin_config.get('positive_color', [0, 255, 0])]
                self.negative_color = [int(float(c)) for c in self.plugin_config.get('negative_color', [255, 0, 0])]
            
            # Crypto customization - check new format first, then old format
            crypto_custom = customization.get('crypto', {})
            if crypto_custom:
                self.crypto_text_color = [int(float(c)) for c in crypto_custom.get('text_color', [255, 215, 0])]
                self.crypto_positive_color = [int(float(c)) for c in crypto_custom.get('positive_color', [0, 255, 0])]
                self.crypto_negative_color = [int(float(c)) for c in crypto_custom.get('negative_color', [255, 0, 0])]
            else:
                # Old format - check crypto object for backward compatibility
                self.crypto_text_color = [int(float(c)) for c in crypto_config.get('text_color', [255, 215, 0])]
                self.crypto_positive_color = [int(float(c)) for c in crypto_config.get('positive_color', [0, 255, 0])]
                self.crypto_negative_color = [int(float(c)) for c in crypto_config.get('negative_color', [255, 0, 0])]
            
            
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
        self.scroll_speed = 1.0  # Pixels per frame
        self.scroll_delay = 0.02
        self.enable_scrolling = True
        self.toggle_chart = False
        self.dynamic_duration = True
        self.min_duration = 30
        self.max_duration = 300
        self.duration_buffer = 0.1
        self.update_interval = 600
        self.text_color = [255, 255, 255]
        self.positive_color = [0, 255, 0]
        self.negative_color = [255, 0, 0]
        self.show_change = True
        self.show_percentage = True
        self.stock_display_format = "{symbol}: ${price} ({change}%)"
        self.crypto_text_color = [255, 215, 0]
        self.crypto_positive_color = [0, 255, 0]
        self.crypto_negative_color = [255, 0, 0]
        self.crypto_show_change = True
        self.crypto_show_percentage = True
        self.crypto_display_format = "{symbol}: ${price} ({change}%)"
        self.stock_symbols = []
        self.stocks_enabled = True
        self.crypto_symbols = []
        self.crypto_update_interval = 600
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
        """Set the scroll speed (pixels per frame, 0.5-5.0)."""
        # Clamp to valid range per schema
        self.scroll_speed = max(0.5, min(5.0, speed))
        self.logger.debug("Scroll speed set to: %.2f pixels per frame", self.scroll_speed)
    
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
            'stocks_enabled': self.stocks_enabled,
            'stocks_count': len(self.stock_symbols),
            'crypto_count': len(self.crypto_symbols),
            'scroll_speed': self.scroll_speed,  # Pixels per frame
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
                    # Accept both int and float, convert to int for validation
                    try:
                        component_int = int(float(component))
                        if not (0 <= component_int <= 255):
                            self.logger.error("%s components must be between 0 and 255", color_name)
                            return False
                    except (ValueError, TypeError):
                        self.logger.error("%s components must be numeric values between 0 and 255", color_name)
                        return False
            
            self.logger.debug("Configuration validation passed")
            return True
            
        except Exception as e:
            self.logger.error("Error validating configuration: %s", e)
            return False
