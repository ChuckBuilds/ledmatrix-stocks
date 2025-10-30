"""
Display Renderer for Stock Ticker Plugin

Handles all display creation, layout, and rendering logic for both
scrolling and static display modes.
"""

from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ImageDraw

# Import common utilities
from src.common import ScrollHelper, LogoHelper, TextHelper


class StockDisplayRenderer:
    """Handles rendering of stock and cryptocurrency displays."""
    
    def __init__(self, config: Dict[str, Any], display_width: int, display_height: int, logger):
        """Initialize the display renderer."""
        self.config = config
        self.display_width = display_width
        self.display_height = display_height
        self.logger = logger
        
        # Display configuration
        self.toggle_chart = config.get('toggle_chart', True)
        self.font_size = config.get('font_size', 10)
        
        # Colors
        self.text_color = tuple(config.get('text_color', [255, 255, 255]))
        self.positive_color = tuple(config.get('positive_color', [0, 255, 0]))
        self.negative_color = tuple(config.get('negative_color', [255, 0, 0]))
        self.crypto_text_color = tuple(config.get('crypto_text_color', [255, 255, 0]))
        self.crypto_positive_color = tuple(config.get('crypto_positive_color', [0, 255, 0]))
        self.crypto_negative_color = tuple(config.get('crypto_negative_color', [255, 0, 0]))
        
        # Initialize helpers
        self.logo_helper = LogoHelper(display_width, display_height, logger=logger)
        self.text_helper = TextHelper(logger=self.logger)
        
        # Initialize scroll helper
        self.scroll_helper = ScrollHelper(display_width, display_height, logger)
        
        # Cache fonts to avoid reloading every time
        self._cached_fonts = None
    
    def _get_fonts(self):
        """Get cached fonts, loading them only once."""
        if self._cached_fonts is None:
            self._cached_fonts = self.text_helper.load_fonts()
        return self._cached_fonts
    
    def create_stock_display(self, symbol: str, data: Dict[str, Any]) -> Image.Image:
        """Create a display image for a single stock or crypto - matching old stock manager layout exactly."""
        # Create a wider image for scrolling - adjust width based on chart toggle
        width = int(self.display_width * (2 if self.toggle_chart else 1.2))  # Much more compact when no chart
        height = self.display_height
        image = Image.new('RGB', (width, height), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        is_crypto = data.get('is_crypto', False)
        
        # Draw large stock/crypto logo on the left
        logo = self._get_stock_logo(symbol, is_crypto)
        if logo:
            # Position logo on the left side with minimal spacing
            logo_x = 2  # Small margin from left edge
            logo_y = (height - logo.height) // 2
            image.paste(logo, (logo_x, logo_y), logo)
        
        # Load fonts - use the same fonts as old stock manager
        fonts = self._get_fonts()
        
        # Create smaller versions of the fonts for symbol and price (matching old stock manager)
        symbol_font = fonts.get('score')  # Use regular font for symbol
        price_font = fonts.get('score')   # Use regular font for price
        change_font = fonts.get('time')   # Use small font for change
        
        # Create text elements
        display_symbol = symbol.replace('-USD', '') if is_crypto else symbol
        symbol_text = display_symbol
        price_text = f"${data['price']:.2f}"
        change_text = f"{data['change']:+.2f} ({data['change']:+.1f}%)"
        
        # Get colors based on change
        if data['change'] >= 0:
            change_color = self.positive_color if not is_crypto else self.crypto_positive_color
        else:
            change_color = self.negative_color if not is_crypto else self.crypto_negative_color
        
        text_color = self.text_color if not is_crypto else self.crypto_text_color
        
        # Calculate text dimensions for proper spacing (matching old stock manager)
        symbol_bbox = draw.textbbox((0, 0), symbol_text, font=symbol_font)
        price_bbox = draw.textbbox((0, 0), price_text, font=price_font)
        change_bbox = draw.textbbox((0, 0), change_text, font=change_font)
        
        # Calculate total height needed - adjust gaps based on chart toggle
        text_gap = 2 if self.toggle_chart else 1  # Reduced gap when no chart
        total_text_height = (symbol_bbox[3] - symbol_bbox[1]) + \
                           (price_bbox[3] - price_bbox[1]) + \
                           (change_bbox[3] - change_bbox[1]) + \
                           (text_gap * 2)  # Account for gaps between elements
        
        # Calculate starting y position to center all text
        start_y = (height - total_text_height) // 2
        
        # Calculate center x position for the column - adjust based on chart toggle
        if self.toggle_chart:
            # When chart is enabled, center text more to the left
            column_x = width // 2.85
        else:
            # When chart is disabled, position text closer to logo for more compact layout
            column_x = width // 1.8
        
        # Draw symbol
        symbol_width = symbol_bbox[2] - symbol_bbox[0]
        symbol_x = column_x - (symbol_width // 2)
        draw.text((symbol_x, start_y), symbol_text, font=symbol_font, fill=text_color)
        
        # Draw price
        price_width = price_bbox[2] - price_bbox[0]
        price_x = column_x - (price_width // 2)
        price_y = start_y + (symbol_bbox[3] - symbol_bbox[1]) + text_gap  # Adjusted gap
        draw.text((price_x, price_y), price_text, font=price_font, fill=text_color)
        
        # Draw change with color based on value
        change_width = change_bbox[2] - change_bbox[0]
        change_x = column_x - (change_width // 2)
        change_y = price_y + (price_bbox[3] - price_bbox[1]) + text_gap  # Adjusted gap
        draw.text((change_x, change_y), change_text, font=change_font, fill=change_color)
        
        # Draw mini chart on the right only if toggle_chart is enabled
        if self.toggle_chart and 'price_history' in data and len(data['price_history']) >= 2:
            self._draw_mini_chart(draw, data['price_history'], width, height, change_color)
        
        return image
    
    def create_static_display(self, symbol: str, data: Dict[str, Any]) -> Image.Image:
        """Create a static display for one stock/crypto (no scrolling)."""
        image = Image.new('RGB', (self.display_width, self.display_height), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        is_crypto = data.get('is_crypto', False)
        
        # Draw logo
        logo = self._get_stock_logo(symbol, is_crypto)
        if logo:
            logo_x = 5
            logo_y = (self.display_height - logo.height) // 2
            image.paste(logo, (logo_x, logo_y), logo)
        
        # Load fonts
        fonts = self._get_fonts()
        symbol_font = fonts.get('score')
        price_font = fonts.get('score')
        change_font = fonts.get('time')
        
        # Create text
        display_symbol = symbol.replace('-USD', '') if is_crypto else symbol
        symbol_text = display_symbol
        price_text = f"${data['price']:.2f}"
        change_text = f"{data['change']:+.2f} ({data['change']:+.1f}%)"
        
        # Get colors
        if data['change'] >= 0:
            change_color = self.positive_color if not is_crypto else self.crypto_positive_color
        else:
            change_color = self.negative_color if not is_crypto else self.crypto_negative_color
        
        text_color = self.text_color if not is_crypto else self.crypto_text_color
        
        # Calculate positions
        symbol_bbox = draw.textbbox((0, 0), symbol_text, font=symbol_font)
        price_bbox = draw.textbbox((0, 0), price_text, font=price_font)
        change_bbox = draw.textbbox((0, 0), change_text, font=change_font)
        
        # Center everything
        center_x = self.display_width // 2
        
        # Draw symbol
        symbol_width = symbol_bbox[2] - symbol_bbox[0]
        symbol_x = center_x - (symbol_width // 2)
        draw.text((symbol_x, 5), symbol_text, font=symbol_font, fill=text_color)
        
        # Draw price
        price_width = price_bbox[2] - price_bbox[0]
        price_x = center_x - (price_width // 2)
        draw.text((price_x, 15), price_text, font=price_font, fill=text_color)
        
        # Draw change
        change_width = change_bbox[2] - change_bbox[0]
        change_x = center_x - (change_width // 2)
        draw.text((change_x, 25), change_text, font=change_font, fill=change_color)
        
        return image
    
    def create_scrolling_display(self, all_data: Dict[str, Any]) -> Image.Image:
        """Create a wide scrolling image with all stocks/crypto."""
        if not all_data:
            return self._create_error_display()
        
        # Calculate total width needed
        stock_displays = []
        total_width = 0
        
        for symbol, data in all_data.items():
            display = self.create_stock_display(symbol, data)
            stock_displays.append(display)
            total_width += display.width
        
        # Add spacing between stocks
        spacing = 20
        total_width += spacing * (len(stock_displays) - 1)
        
        # Create scrolling image
        scrolling_image = Image.new('RGB', (total_width, self.display_height), (0, 0, 0))
        
        # Paste all stock displays
        x_offset = 0
        for display in stock_displays:
            scrolling_image.paste(display, (x_offset, 0))
            x_offset += display.width + spacing
        
        return scrolling_image
    
    def _get_stock_logo(self, symbol: str, is_crypto: bool = False) -> Optional[Image.Image]:
        """Get stock or crypto logo image - matching old stock manager sizing."""
        try:
            if is_crypto:
                # Try crypto icons first
                logo_path = f"assets/stocks/crypto_icons/{symbol}.png"
            else:
                # Try stock icons
                logo_path = f"assets/stocks/ticker_icons/{symbol}.png"
            
            # Use same sizing as old stock manager (display_width/1.2, display_height/1.2)
            max_size = min(int(self.display_width / 1.2), int(self.display_height / 1.2))
            return self.logo_helper.load_logo(symbol, logo_path, max_size, max_size)
            
        except (OSError, IOError) as e:
            self.logger.warning("Error loading logo for %s: %s", symbol, e)
            return None
    
    def _draw_mini_chart(self, draw: ImageDraw.Draw, price_history: List[Dict], 
                        width: int, height: int, color: Tuple[int, int, int]) -> None:
        """Draw a mini price chart on the right side of the display."""
        if len(price_history) < 2:
            return
        
        # Chart dimensions
        chart_width = width // 4
        chart_height = height - 4
        chart_x = width - chart_width - 2
        chart_y = 2
        
        # Extract prices
        prices = [point['price'] for point in price_history if 'price' in point]
        if len(prices) < 2:
            return
        
        # Normalize prices to chart height
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        
        if price_range == 0:
            # All prices are the same, draw a horizontal line
            y = chart_y + chart_height // 2
            draw.line([(chart_x, y), (chart_x + chart_width, y)], fill=color, width=1)
            return
        
        # Draw chart line
        points = []
        for i, price in enumerate(prices):
            x = chart_x + (i * chart_width) // (len(prices) - 1)
            y = chart_y + chart_height - int(((price - min_price) / price_range) * chart_height)
            points.append((x, y))
        
        if len(points) > 1:
            draw.line(points, fill=color, width=1)
    
    def _create_error_display(self) -> Image.Image:
        """Create an error display when no data is available."""
        image = Image.new('RGB', (self.display_width, self.display_height), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Load fonts
        fonts = self._get_fonts()
        error_font = fonts.get('score')
        
        # Draw error message
        error_text = "No Data Available"
        bbox = draw.textbbox((0, 0), error_text, font=error_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (self.display_width - text_width) // 2
        y = (self.display_height - text_height) // 2
        
        draw.text((x, y), error_text, font=error_font, fill=(255, 0, 0))
        
        return image
    
    def set_toggle_chart(self, enabled: bool) -> None:
        """Set whether to show mini charts."""
        self.toggle_chart = enabled
        self.logger.debug("Chart toggle set to: %s", enabled)
    
    def get_scroll_helper(self) -> ScrollHelper:
        """Get the scroll helper instance."""
        return self.scroll_helper
