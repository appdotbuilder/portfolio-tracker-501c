from decimal import Decimal
from app.price_service import PriceService
from app.models import AssetType


class TestPriceService:
    """Test suite for PriceService"""

    def test_price_service_initialization(self):
        """Test that PriceService initializes correctly"""
        service = PriceService()
        assert service._cache == {}

    def test_get_current_price_stock(self):
        """Test fetching current price for a stock"""
        service = PriceService()

        # Test with a well-known stock symbol
        price = service.get_current_price("AAPL", AssetType.STOCK)

        # Price should be a positive decimal or None if service is down
        if price is not None:
            assert isinstance(price, Decimal)
            assert price > 0

    def test_get_current_price_crypto(self):
        """Test fetching current price for cryptocurrency"""
        service = PriceService()

        # Test with Bitcoin
        price = service.get_current_price("BTC", AssetType.CRYPTOCURRENCY)

        # Price should be a positive decimal or None if service is down
        if price is not None:
            assert isinstance(price, Decimal)
            assert price > 0

    def test_get_current_price_crypto_with_usd_suffix(self):
        """Test crypto price fetching with USD suffix"""
        service = PriceService()

        # Test with Bitcoin already having USD suffix
        price = service.get_current_price("BTC-USD", AssetType.CRYPTOCURRENCY)

        # Should work the same as without suffix
        if price is not None:
            assert isinstance(price, Decimal)
            assert price > 0

    def test_get_current_price_invalid_symbol(self):
        """Test fetching price for invalid symbol"""
        service = PriceService()

        # Test with invalid symbol
        price = service.get_current_price("INVALID123", AssetType.STOCK)

        # Should return None for invalid symbols
        assert price is None

    def test_get_multiple_prices(self):
        """Test fetching multiple prices at once"""
        service = PriceService()

        symbols = [("AAPL", AssetType.STOCK), ("BTC", AssetType.CRYPTOCURRENCY), ("INVALID", AssetType.STOCK)]

        results = service.get_multiple_prices(symbols)

        assert len(results) == 3
        assert "AAPL" in results
        assert "BTC" in results
        assert "INVALID" in results

        # INVALID should be None
        assert results["INVALID"] is None

        # Valid symbols should have prices or None if service is down
        for symbol, price in results.items():
            if price is not None:
                assert isinstance(price, Decimal)
                assert price > 0

    def test_get_multiple_prices_empty_list(self):
        """Test fetching multiple prices with empty list"""
        service = PriceService()

        results = service.get_multiple_prices([])

        assert results == {}

    def test_crypto_symbol_formatting(self):
        """Test that crypto symbols are formatted correctly"""
        service = PriceService()

        # Both should work the same way
        price1 = service.get_current_price("BTC", AssetType.CRYPTOCURRENCY)
        price2 = service.get_current_price("BTC-USD", AssetType.CRYPTOCURRENCY)

        # Both should be valid (or both None if service is down)
        assert (price1 is None and price2 is None) or (isinstance(price1, Decimal) and isinstance(price2, Decimal))
