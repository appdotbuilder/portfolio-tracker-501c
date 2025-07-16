from decimal import Decimal
from typing import Dict, Optional
import yfinance as yf
from app.models import AssetType


class PriceService:
    """Service for fetching real-time asset prices using yfinance"""

    def __init__(self):
        self._cache: Dict[str, Decimal] = {}

    def get_current_price(self, symbol: str, asset_type: AssetType) -> Optional[Decimal]:
        """
        Get current price for a given asset symbol

        Args:
            symbol: Asset symbol (e.g., 'AAPL', 'BTC-USD')
            asset_type: Type of asset (stock or crypto)

        Returns:
            Current price as Decimal or None if not found
        """
        try:
            # For crypto, ensure proper symbol format
            if asset_type == AssetType.CRYPTOCURRENCY:
                if not symbol.endswith("-USD"):
                    symbol = f"{symbol}-USD"

            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Try different price fields depending on what's available
            price_fields = ["regularMarketPrice", "currentPrice", "price", "regularMarketPreviousClose"]

            for field in price_fields:
                if field in info and info[field] is not None:
                    return Decimal(str(info[field]))

            # If info doesn't have price, try fast_info
            if hasattr(ticker, "fast_info"):
                fast_info = ticker.fast_info
                if "last_price" in fast_info:
                    return Decimal(str(fast_info["last_price"]))

            # Last resort: get latest price from history
            hist = ticker.history(period="1d")
            if not hist.empty:
                return Decimal(str(hist["Close"].iloc[-1]))

        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None

        return None

    def get_multiple_prices(self, symbols: list[tuple[str, AssetType]]) -> Dict[str, Optional[Decimal]]:
        """
        Get current prices for multiple assets

        Args:
            symbols: List of (symbol, asset_type) tuples

        Returns:
            Dictionary mapping symbol to price or None if not found
        """
        results = {}
        for symbol, asset_type in symbols:
            results[symbol] = self.get_current_price(symbol, asset_type)
        return results


# Global price service instance
price_service = PriceService()
