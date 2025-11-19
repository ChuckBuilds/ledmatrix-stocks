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
        
        # Colors for stocks (top level)
        self.text_color = tuple(config.get('text_color', [255, 255, 255]))
        self.positive_color = tuple(config.get('positive_color', [0, 255, 0]))
        self.negative_color = tuple(config.get('negative_color', [255, 0, 0]))
        
        # Colors for crypto (nested under 'crypto' object per schema)
        crypto_config = config.get('crypto', {})
        self.crypto_text_color = tuple(crypto_config.get('text_color', [255, 215, 0]))
        self.crypto_positive_color = tuple(crypto_config.get('positive_color', [0, 255, 0]))
        self.crypto_negative_color = tuple(crypto_config.get('negative_color', [255, 0, 0]))
        
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
        # Match old stock_manager: width = int(self.display_manager.matrix.width * (2 if self.toggle_chart else 1.5))
        # Ensure dimensions are integers
        width = int(self.display_width * (2 if self.toggle_chart else 1.5))
        height = int(self.display_height)
        image = Image.new('RGB', (width, height), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        is_crypto = data.get('is_crypto', False)
        
        # Draw large stock/crypto logo on the left
        logo = self._get_stock_logo(symbol, is_crypto)
        if logo:
            # Position logo on the left side with minimal spacing - matching old stock_manager
            # Ensure positions are integers
            logo_x = 2  # Small margin from left edge
            logo_y = int((height - logo.height) // 2)
            image.paste(logo, (int(logo_x), int(logo_y)), logo)
        
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
        # Match old stock_manager: text_gap = 2 if self.toggle_chart else 1
        text_gap = 2 if self.toggle_chart else 1
        total_text_height = (symbol_bbox[3] - symbol_bbox[1]) + \
                           (price_bbox[3] - price_bbox[1]) + \
                           (change_bbox[3] - change_bbox[1]) + \
                           (text_gap * 2)  # Account for gaps between elements
        
        # Calculate starting y position to center all text
        start_y = (height - total_text_height) // 2
        
        # Calculate center x position for the column - adjust based on chart toggle
        # Match old stock_manager exactly
        if self.toggle_chart:
            # When chart is enabled, center text more to the left
            column_x = width // 2.85
        else:
            # When chart is disabled, position text with more space from logo
            column_x = width // 2.2
        
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
        # Ensure dimensions are integers
        image = Image.new('RGB', (int(self.display_width), int(self.display_height)), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        is_crypto = data.get('is_crypto', False)
        
        # Draw logo
        logo = self._get_stock_logo(symbol, is_crypto)
        if logo:
            # Ensure positions are integers
            logo_x = 5
            logo_y = int((int(self.display_height) - logo.height) // 2)
            image.paste(logo, (int(logo_x), int(logo_y)), logo)
        
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
        
        # Center everything - ensure integer
        center_x = int(self.display_width) // 2
        
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
        """Create a wide scrolling image with all stocks/crypto - matching old stock_manager spacing."""
        if not all_data:
            return self._create_error_display()
        
        # Calculate total width needed - match old stock_manager spacing logic
        # Ensure dimensions are integers
        width = int(self.display_width)
        height = int(self.display_height)
        
        # Create individual stock displays
        stock_displays = []
        for symbol, data in all_data.items():
            display = self.create_stock_display(symbol, data)
            stock_displays.append(display)
        
        # Calculate spacing - match old stock_manager exactly
        # Old code: stock_gap = width // 6, element_gap = width // 8
        stock_gap = width // 6  # Reduced gap between stocks
        element_gap = width // 8  # Reduced gap between elements within a stock
        
        # Calculate total width - match old stock_manager calculation
        # Old code: total_width = sum(width * 2 for _ in symbols) + stock_gap * (len(symbols) - 1) + element_gap * (len(symbols) * 2 - 1)
        # But each display already has its own width (width * 2 or width * 1.5), so we sum display widths
        # Ensure all values are integers
        total_width = sum(int(display.width) for display in stock_displays)
        total_width += int(stock_gap) * (len(stock_displays) - 1)
        total_width += int(element_gap) * (len(stock_displays) * 2 - 1)
        
        # Create scrolling image - ensure dimensions are integers
        scrolling_image = Image.new('RGB', (int(total_width), int(height)), (0, 0, 0))
        
        # Paste all stock displays with spacing - match old stock_manager logic
        # Old code: current_x = width (starts with display width gap)
        current_x = int(width)  # Add initial gap before the first stock
        
        for i, display in enumerate(stock_displays):
            # Paste this stock image into the full image - ensure position is integer tuple
            scrolling_image.paste(display, (int(current_x), 0))
            
            # Move to next position with consistent spacing
            # Old code: current_x += width * 2 + element_gap
            current_x += int(display.width) + int(element_gap)
            
            # Add extra gap between stocks (except after the last stock)
            if i < len(stock_displays) - 1:
                current_x += int(stock_gap)
        
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
        """Draw a mini price chart on the right side of the display - matching old stock_manager exactly."""
        if len(price_history) < 2:
            return
        
        # Chart dimensions - match old stock_manager exactly
        # Old code: chart_width = int(width // 2.5), chart_height = height // 1.5
        # Ensure all dimensions are integers
        chart_width = int(width // 2.5)  # Reduced from width//2.5 to prevent overlap
        chart_height = int(height // 1.5)
        chart_x = int(width - chart_width - 4)  # 4px margin from right edge
        chart_y = int((height - chart_height) // 2)
        
        # Extract prices - match old stock_manager exactly
        prices = [point['price'] for point in price_history if 'price' in point]
        if len(prices) < 2:
            return
        
        # Find min and max prices for scaling - match old stock_manager
        min_price = min(prices)
        max_price = max(prices)
        
        # Add padding to avoid flat lines when prices are very close - match old stock_manager
        price_range = max_price - min_price
        if price_range < 0.01:
            min_price -= 0.01
            max_price += 0.01
            price_range = 0.02
        
        if price_range == 0:
            # All prices are the same, draw a horizontal line
            y = chart_y + chart_height // 2
            draw.line([(chart_x, y), (chart_x + chart_width, y)], fill=color, width=1)
            return
        
        # Calculate points for the line - match old stock_manager exactly
        # Ensure all coordinates are integers
        points = []
        for i, price in enumerate(prices):
            x = int(chart_x + (i * chart_width) // (len(prices) - 1))
            y = int(chart_y + chart_height - int(((price - min_price) / price_range) * chart_height))
            points.append((x, y))
        
        # Draw lines between points - match old stock_manager
        if len(points) > 1:
            for i in range(len(points) - 1):
                draw.line([points[i], points[i + 1]], fill=color, width=1)
    
    def _create_error_display(self) -> Image.Image:
        """Create an error display when no data is available."""
        # Ensure dimensions are integers
        image = Image.new('RGB', (int(self.display_width), int(self.display_height)), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Load fonts
        fonts = self._get_fonts()
        error_font = fonts.get('score')
        
        # Draw error message
        error_text = "No Data Available"
        bbox = draw.textbbox((0, 0), error_text, font=error_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Ensure dimensions are integers
        x = (int(self.display_width) - text_width) // 2
        y = (int(self.display_height) - text_height) // 2
        
        draw.text((x, y), error_text, font=error_font, fill=(255, 0, 0))
        
        return image
    
    def set_toggle_chart(self, enabled: bool) -> None:
        """Set whether to show mini charts."""
        self.toggle_chart = enabled
        self.logger.debug("Chart toggle set to: %s", enabled)
    
    def get_scroll_helper(self) -> ScrollHelper:
        """Get the scroll helper instance."""
        return self.scroll_helper
