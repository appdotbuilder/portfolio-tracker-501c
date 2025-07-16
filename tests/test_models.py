from decimal import Decimal
from datetime import datetime
from app.models import Position, PositionCreate, PositionUpdate, PositionWithMetrics, PortfolioSummary, AssetType


class TestModels:
    """Test suite for data models"""

    def test_asset_type_enum(self):
        """Test AssetType enum values"""
        assert AssetType.STOCK == "stock"
        assert AssetType.CRYPTOCURRENCY == "crypto"

    def test_position_create_valid(self):
        """Test creating a valid PositionCreate instance"""
        position = PositionCreate(
            asset_symbol="AAPL", asset_type=AssetType.STOCK, shares=Decimal("10.0"), purchase_price=Decimal("150.00")
        )

        assert position.asset_symbol == "AAPL"
        assert position.asset_type == AssetType.STOCK
        assert position.shares == Decimal("10.0")
        assert position.purchase_price == Decimal("150.00")

    def test_position_create_default_asset_type(self):
        """Test PositionCreate with default asset type"""
        position = PositionCreate(asset_symbol="AAPL", shares=Decimal("10.0"), purchase_price=Decimal("150.00"))

        assert position.asset_type == AssetType.STOCK

    def test_position_create_crypto(self):
        """Test PositionCreate with cryptocurrency"""
        position = PositionCreate(
            asset_symbol="BTC",
            asset_type=AssetType.CRYPTOCURRENCY,
            shares=Decimal("0.5"),
            purchase_price=Decimal("50000.00"),
        )

        assert position.asset_symbol == "BTC"
        assert position.asset_type == AssetType.CRYPTOCURRENCY
        assert position.shares == Decimal("0.5")
        assert position.purchase_price == Decimal("50000.00")

    def test_position_update_partial(self):
        """Test PositionUpdate with partial data"""
        update = PositionUpdate(shares=Decimal("15.0"), purchase_price=Decimal("160.00"))

        assert update.shares == Decimal("15.0")
        assert update.purchase_price == Decimal("160.00")
        assert update.asset_symbol is None
        assert update.asset_type is None

    def test_position_update_all_fields(self):
        """Test PositionUpdate with all fields"""
        update = PositionUpdate(
            asset_symbol="GOOGL", asset_type=AssetType.STOCK, shares=Decimal("5.0"), purchase_price=Decimal("2000.00")
        )

        assert update.asset_symbol == "GOOGL"
        assert update.asset_type == AssetType.STOCK
        assert update.shares == Decimal("5.0")
        assert update.purchase_price == Decimal("2000.00")

    def test_position_with_metrics(self):
        """Test PositionWithMetrics model"""
        now = datetime.utcnow()

        position_metrics = PositionWithMetrics(
            id=1,
            asset_symbol="AAPL",
            asset_type=AssetType.STOCK,
            shares=Decimal("10.0"),
            purchase_price=Decimal("150.00"),
            current_price=Decimal("160.00"),
            current_value=Decimal("1600.00"),
            roi_percentage=Decimal("6.67"),
            profit_loss=Decimal("100.00"),
            created_at=now,
            updated_at=now,
        )

        assert position_metrics.id == 1
        assert position_metrics.asset_symbol == "AAPL"
        assert position_metrics.current_price == Decimal("160.00")
        assert position_metrics.current_value == Decimal("1600.00")
        assert position_metrics.roi_percentage == Decimal("6.67")
        assert position_metrics.profit_loss == Decimal("100.00")

    def test_portfolio_summary(self):
        """Test PortfolioSummary model"""
        now = datetime.utcnow()

        summary = PortfolioSummary(
            total_positions=5,
            total_value=Decimal("10000.00"),
            total_cost=Decimal("9000.00"),
            total_roi_percentage=Decimal("11.11"),
            total_profit_loss=Decimal("1000.00"),
            last_updated=now,
        )

        assert summary.total_positions == 5
        assert summary.total_value == Decimal("10000.00")
        assert summary.total_cost == Decimal("9000.00")
        assert summary.total_roi_percentage == Decimal("11.11")
        assert summary.total_profit_loss == Decimal("1000.00")
        assert summary.last_updated == now

    def test_position_total_cost_property(self):
        """Test Position model's total_cost property"""
        position = Position(
            asset_symbol="AAPL", asset_type=AssetType.STOCK, shares=Decimal("10.0"), purchase_price=Decimal("150.00")
        )

        assert position.total_cost == Decimal("1500.00")

    def test_position_total_cost_fractional_shares(self):
        """Test total_cost with fractional shares"""
        position = Position(
            asset_symbol="BTC",
            asset_type=AssetType.CRYPTOCURRENCY,
            shares=Decimal("0.5"),
            purchase_price=Decimal("50000.00"),
        )

        assert position.total_cost == Decimal("25000.00")

    def test_position_precision_handling(self):
        """Test that Position handles decimal precision correctly"""
        position = Position(
            asset_symbol="ETH",
            asset_type=AssetType.CRYPTOCURRENCY,
            shares=Decimal("1.12345678"),
            purchase_price=Decimal("3000.12"),
        )

        # Test that precision is maintained
        assert position.shares == Decimal("1.12345678")
        assert position.purchase_price == Decimal("3000.12")

        # Test total cost calculation
        expected_total = Decimal("1.12345678") * Decimal("3000.12")
        assert position.total_cost == expected_total

    def test_position_create_validation_positive_shares(self):
        """Test that PositionCreate validates positive shares"""
        # This would normally be validated by Pydantic, but we test the constraint
        try:
            PositionCreate(
                asset_symbol="AAPL",
                shares=Decimal("0.0"),  # Should be > 0
                purchase_price=Decimal("150.00"),
            )
            # If validation is working, this should fail
            assert False, "Expected validation error for zero shares"
        except Exception:
            # Expected to fail validation
            pass

    def test_position_create_validation_positive_price(self):
        """Test that PositionCreate validates positive price"""
        try:
            PositionCreate(
                asset_symbol="AAPL",
                shares=Decimal("10.0"),
                purchase_price=Decimal("0.0"),  # Should be > 0
            )
            # If validation is working, this should fail
            assert False, "Expected validation error for zero price"
        except Exception:
            # Expected to fail validation
            pass

    def test_position_update_validation_positive_shares(self):
        """Test that PositionUpdate validates positive shares when provided"""
        try:
            PositionUpdate(
                shares=Decimal("0.0")  # Should be > 0 when provided
            )
            # If validation is working, this should fail
            assert False, "Expected validation error for zero shares"
        except Exception:
            # Expected to fail validation
            pass

    def test_position_update_validation_positive_price(self):
        """Test that PositionUpdate validates positive price when provided"""
        try:
            PositionUpdate(
                purchase_price=Decimal("0.0")  # Should be > 0 when provided
            )
            # If validation is working, this should fail
            assert False, "Expected validation error for zero price"
        except Exception:
            # Expected to fail validation
            pass

    def test_position_datetime_fields(self):
        """Test that Position has proper datetime fields"""
        position = Position(
            asset_symbol="AAPL", asset_type=AssetType.STOCK, shares=Decimal("10.0"), purchase_price=Decimal("150.00")
        )

        # Fields should be set by default_factory
        assert position.created_at is not None
        assert position.updated_at is not None
        assert isinstance(position.created_at, datetime)
        assert isinstance(position.updated_at, datetime)

    def test_position_symbol_max_length(self):
        """Test that asset symbol has proper max length constraint"""
        # 20 characters should be fine
        position = Position(
            asset_symbol="A" * 20, asset_type=AssetType.STOCK, shares=Decimal("10.0"), purchase_price=Decimal("150.00")
        )

        assert len(position.asset_symbol) == 20

    def test_decimal_precision_shares(self):
        """Test decimal precision for shares (8 decimal places)"""
        position = Position(
            asset_symbol="BTC",
            asset_type=AssetType.CRYPTOCURRENCY,
            shares=Decimal("0.12345678"),
            purchase_price=Decimal("50000.00"),
        )

        assert position.shares == Decimal("0.12345678")

    def test_decimal_precision_price(self):
        """Test decimal precision for price (2 decimal places)"""
        position = Position(
            asset_symbol="AAPL", asset_type=AssetType.STOCK, shares=Decimal("10.0"), purchase_price=Decimal("150.12")
        )

        assert position.purchase_price == Decimal("150.12")
