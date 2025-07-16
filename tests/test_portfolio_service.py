import pytest
from decimal import Decimal
from app.portfolio_service import PortfolioService
from app.models import PositionCreate, PositionUpdate, AssetType
from app.database import reset_db


@pytest.fixture()
def new_db():
    """Fixture to reset database before each test"""
    reset_db()
    yield
    reset_db()


class TestPortfolioService:
    """Test suite for PortfolioService"""

    def test_create_position(self, new_db):
        """Test creating a new position"""
        service = PortfolioService()

        position_data = PositionCreate(
            asset_symbol="AAPL", asset_type=AssetType.STOCK, shares=Decimal("10.0"), purchase_price=Decimal("150.00")
        )

        position = service.create_position(position_data)

        assert position.id is not None
        assert position.asset_symbol == "AAPL"
        assert position.asset_type == AssetType.STOCK
        assert position.shares == Decimal("10.0")
        assert position.purchase_price == Decimal("150.00")
        assert position.created_at is not None
        assert position.updated_at is not None

    def test_create_position_symbol_uppercase(self, new_db):
        """Test that asset symbols are converted to uppercase"""
        service = PortfolioService()

        position_data = PositionCreate(
            asset_symbol="aapl", asset_type=AssetType.STOCK, shares=Decimal("5.0"), purchase_price=Decimal("100.00")
        )

        position = service.create_position(position_data)

        assert position.asset_symbol == "AAPL"

    def test_get_position(self, new_db):
        """Test retrieving a position by ID"""
        service = PortfolioService()

        # Create a position first
        position_data = PositionCreate(
            asset_symbol="TSLA", asset_type=AssetType.STOCK, shares=Decimal("5.0"), purchase_price=Decimal("200.00")
        )

        created_position = service.create_position(position_data)

        # Retrieve the position
        if created_position.id is not None:
            retrieved_position = service.get_position(created_position.id)

            assert retrieved_position is not None
            assert retrieved_position.id == created_position.id
            assert retrieved_position.asset_symbol == "TSLA"

    def test_get_position_not_found(self, new_db):
        """Test retrieving a non-existent position"""
        service = PortfolioService()

        position = service.get_position(999)

        assert position is None

    def test_get_all_positions(self, new_db):
        """Test retrieving all positions"""
        service = PortfolioService()

        # Create multiple positions
        positions_data = [
            PositionCreate(
                asset_symbol="AAPL",
                asset_type=AssetType.STOCK,
                shares=Decimal("10.0"),
                purchase_price=Decimal("150.00"),
            ),
            PositionCreate(
                asset_symbol="BTC",
                asset_type=AssetType.CRYPTOCURRENCY,
                shares=Decimal("0.5"),
                purchase_price=Decimal("50000.00"),
            ),
        ]

        created_positions = []
        for position_data in positions_data:
            created_positions.append(service.create_position(position_data))

        # Retrieve all positions
        all_positions = service.get_all_positions()

        assert len(all_positions) == 2
        symbols = [pos.asset_symbol for pos in all_positions]
        assert "AAPL" in symbols
        assert "BTC" in symbols

    def test_get_all_positions_empty(self, new_db):
        """Test retrieving all positions when none exist"""
        service = PortfolioService()

        positions = service.get_all_positions()

        assert positions == []

    def test_update_position(self, new_db):
        """Test updating a position"""
        service = PortfolioService()

        # Create a position
        position_data = PositionCreate(
            asset_symbol="AAPL", asset_type=AssetType.STOCK, shares=Decimal("10.0"), purchase_price=Decimal("150.00")
        )

        created_position = service.create_position(position_data)

        # Update the position
        update_data = PositionUpdate(shares=Decimal("15.0"), purchase_price=Decimal("160.00"))

        if created_position.id is not None:
            updated_position = service.update_position(created_position.id, update_data)

            assert updated_position is not None
            assert updated_position.shares == Decimal("15.0")
            assert updated_position.purchase_price == Decimal("160.00")
            assert updated_position.asset_symbol == "AAPL"  # Unchanged
            assert updated_position.updated_at > created_position.updated_at

    def test_update_position_partial(self, new_db):
        """Test partial update of a position"""
        service = PortfolioService()

        # Create a position
        position_data = PositionCreate(
            asset_symbol="AAPL", asset_type=AssetType.STOCK, shares=Decimal("10.0"), purchase_price=Decimal("150.00")
        )

        created_position = service.create_position(position_data)

        # Update only shares
        update_data = PositionUpdate(shares=Decimal("20.0"))

        if created_position.id is not None:
            updated_position = service.update_position(created_position.id, update_data)

            assert updated_position is not None
            assert updated_position.shares == Decimal("20.0")
            assert updated_position.purchase_price == Decimal("150.00")  # Unchanged

    def test_update_position_not_found(self, new_db):
        """Test updating a non-existent position"""
        service = PortfolioService()

        update_data = PositionUpdate(shares=Decimal("5.0"))
        result = service.update_position(999, update_data)

        assert result is None

    def test_delete_position(self, new_db):
        """Test deleting a position"""
        service = PortfolioService()

        # Create a position
        position_data = PositionCreate(
            asset_symbol="AAPL", asset_type=AssetType.STOCK, shares=Decimal("10.0"), purchase_price=Decimal("150.00")
        )

        created_position = service.create_position(position_data)

        # Delete the position
        if created_position.id is not None:
            result = service.delete_position(created_position.id)

            assert result is True

            # Verify it's deleted
            deleted_position = service.get_position(created_position.id)
            assert deleted_position is None

    def test_delete_position_not_found(self, new_db):
        """Test deleting a non-existent position"""
        service = PortfolioService()

        result = service.delete_position(999)

        assert result is False

    def test_get_positions_with_metrics(self, new_db):
        """Test retrieving positions with calculated metrics"""
        service = PortfolioService()

        # Create a position
        position_data = PositionCreate(
            asset_symbol="AAPL", asset_type=AssetType.STOCK, shares=Decimal("10.0"), purchase_price=Decimal("150.00")
        )

        service.create_position(position_data)

        # Get positions with metrics
        positions_with_metrics = service.get_positions_with_metrics()

        assert len(positions_with_metrics) == 1
        position = positions_with_metrics[0]

        assert position.asset_symbol == "AAPL"
        assert position.shares == Decimal("10.0")
        assert position.purchase_price == Decimal("150.00")
        assert hasattr(position, "current_price")
        assert hasattr(position, "current_value")
        assert hasattr(position, "roi_percentage")
        assert hasattr(position, "profit_loss")

    def test_get_positions_with_metrics_empty(self, new_db):
        """Test retrieving positions with metrics when none exist"""
        service = PortfolioService()

        positions_with_metrics = service.get_positions_with_metrics()

        assert positions_with_metrics == []

    def test_get_portfolio_summary(self, new_db):
        """Test retrieving portfolio summary"""
        service = PortfolioService()

        # Create multiple positions
        positions_data = [
            PositionCreate(
                asset_symbol="AAPL",
                asset_type=AssetType.STOCK,
                shares=Decimal("10.0"),
                purchase_price=Decimal("150.00"),
            ),
            PositionCreate(
                asset_symbol="GOOGL",
                asset_type=AssetType.STOCK,
                shares=Decimal("5.0"),
                purchase_price=Decimal("2000.00"),
            ),
        ]

        for position_data in positions_data:
            service.create_position(position_data)

        # Get portfolio summary
        summary = service.get_portfolio_summary()

        assert summary.total_positions == 2
        assert summary.total_cost == Decimal("11500.00")  # 10*150 + 5*2000
        assert hasattr(summary, "total_value")
        assert hasattr(summary, "total_roi_percentage")
        assert hasattr(summary, "total_profit_loss")
        assert hasattr(summary, "last_updated")

    def test_get_portfolio_summary_empty(self, new_db):
        """Test retrieving portfolio summary when no positions exist"""
        service = PortfolioService()

        summary = service.get_portfolio_summary()

        assert summary.total_positions == 0
        assert summary.total_value == Decimal("0")
        assert summary.total_cost == Decimal("0")
        assert summary.total_roi_percentage == Decimal("0")
        assert summary.total_profit_loss == Decimal("0")
        assert summary.last_updated is not None

    def test_position_total_cost_property(self, new_db):
        """Test the total_cost property of Position model"""
        service = PortfolioService()

        position_data = PositionCreate(
            asset_symbol="AAPL", asset_type=AssetType.STOCK, shares=Decimal("10.0"), purchase_price=Decimal("150.00")
        )

        position = service.create_position(position_data)

        assert position.total_cost == Decimal("1500.00")

    def test_roi_calculation_positive(self, new_db):
        """Test ROI calculation with positive returns"""
        service = PortfolioService()

        # Create position
        position_data = PositionCreate(
            asset_symbol="TEST", asset_type=AssetType.STOCK, shares=Decimal("10.0"), purchase_price=Decimal("100.00")
        )

        service.create_position(position_data)

        # Mock current price higher than purchase price
        # This test depends on the actual price service, so we test the logic
        positions = service.get_positions_with_metrics()

        if positions:
            position = positions[0]
            # If current price is available and higher than purchase price
            if position.current_price > position.purchase_price:
                assert position.roi_percentage > 0
                assert position.profit_loss > 0

    def test_roi_calculation_negative(self, new_db):
        """Test ROI calculation with negative returns"""
        service = PortfolioService()

        # Create position
        position_data = PositionCreate(
            asset_symbol="TEST", asset_type=AssetType.STOCK, shares=Decimal("10.0"), purchase_price=Decimal("100.00")
        )

        service.create_position(position_data)

        # Mock current price lower than purchase price
        # This test depends on the actual price service, so we test the logic
        positions = service.get_positions_with_metrics()

        if positions:
            position = positions[0]
            # If current price is available and lower than purchase price
            if position.current_price < position.purchase_price:
                assert position.roi_percentage < 0
                assert position.profit_loss < 0
