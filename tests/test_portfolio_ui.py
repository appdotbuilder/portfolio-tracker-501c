import pytest
from decimal import Decimal
from nicegui.testing import User
from app.database import reset_db
from app.models import PositionCreate, AssetType
from app.portfolio_service import portfolio_service


@pytest.fixture()
def new_db():
    """Fixture to reset database before each test"""
    reset_db()
    yield
    reset_db()


async def test_portfolio_page_loads(user: User, new_db) -> None:
    """Test that the portfolio page loads successfully"""
    await user.open("/")
    await user.should_see("Portfolio Tracker")
    await user.should_see("Portfolio Summary")
    await user.should_see("Add New Position")


async def test_add_position_form_elements(user: User, new_db) -> None:
    """Test that the add position form has all required elements"""
    await user.open("/")

    # Check form elements exist
    await user.should_see("Asset Symbol")
    await user.should_see("Asset Type")
    await user.should_see("Number of Shares/Units")
    await user.should_see("Purchase Price")
    await user.should_see("Add Position")
    await user.should_see("Clear")


async def test_empty_portfolio_message(user: User, new_db) -> None:
    """Test that empty portfolio shows appropriate message"""
    await user.open("/")

    # Should see empty state message
    await user.should_see("No positions found")


async def test_portfolio_with_positions(user: User, new_db) -> None:
    """Test portfolio display with existing positions"""
    # Create a position directly in the database
    position_data = PositionCreate(
        asset_symbol="AAPL", asset_type=AssetType.STOCK, shares=Decimal("10.0"), purchase_price=Decimal("150.00")
    )

    portfolio_service.create_position(position_data)

    await user.open("/")

    # Should see the position in the table
    await user.should_see("AAPL")
    await user.should_see("Stock")


async def test_portfolio_summary_display(user: User, new_db) -> None:
    """Test that portfolio summary displays correctly"""
    # Create multiple positions
    positions = [
        PositionCreate(
            asset_symbol="AAPL", asset_type=AssetType.STOCK, shares=Decimal("10.0"), purchase_price=Decimal("150.00")
        ),
        PositionCreate(
            asset_symbol="GOOGL", asset_type=AssetType.STOCK, shares=Decimal("5.0"), purchase_price=Decimal("2000.00")
        ),
    ]

    for position_data in positions:
        portfolio_service.create_position(position_data)

    await user.open("/")

    # Should see portfolio summary
    await user.should_see("Portfolio Summary")
    await user.should_see("Total Positions")
    await user.should_see("Total Value")
    await user.should_see("Total Cost")
    await user.should_see("Total ROI")
    await user.should_see("P&L")

    # Should show 2 positions
    await user.should_see("2")  # Total positions


async def test_refresh_button_exists(user: User, new_db) -> None:
    """Test that refresh button exists and is clickable"""
    await user.open("/")

    await user.should_see("Refresh Data")

    # Click refresh button
    user.find("Refresh Data").click()


async def test_auto_refresh_toggle(user: User, new_db) -> None:
    """Test auto refresh toggle functionality"""
    await user.open("/")

    # Should see auto refresh button
    await user.should_see("Auto Refresh")


async def test_position_table_columns(user: User, new_db) -> None:
    """Test that position table has all required columns"""
    # Create a position first
    position_data = PositionCreate(
        asset_symbol="AAPL", asset_type=AssetType.STOCK, shares=Decimal("10.0"), purchase_price=Decimal("150.00")
    )

    portfolio_service.create_position(position_data)

    await user.open("/")

    # Check for key table elements
    await user.should_see("Symbol")
    await user.should_see("Type")
    await user.should_see("Shares")
    await user.should_see("Purchase Price")
    await user.should_see("ROI")


async def test_controls_section(user: User, new_db) -> None:
    """Test that controls section exists with expected buttons"""
    await user.open("/")

    await user.should_see("Controls")
    await user.should_see("Refresh Data")
    await user.should_see("Auto Refresh")


async def test_responsive_layout(user: User, new_db) -> None:
    """Test that the layout is responsive and has proper styling"""
    await user.open("/")

    # Check for key layout elements
    await user.should_see("Portfolio Tracker")  # Header
    await user.should_see("Portfolio Summary")  # Summary section
    await user.should_see("Add New Position")  # Form section
    await user.should_see("Portfolio Positions")  # Table section


async def test_crypto_position_display(user: User, new_db) -> None:
    """Test that crypto positions display correctly"""
    # Create a crypto position
    position_data = PositionCreate(
        asset_symbol="BTC",
        asset_type=AssetType.CRYPTOCURRENCY,
        shares=Decimal("0.5"),
        purchase_price=Decimal("50000.00"),
    )

    portfolio_service.create_position(position_data)

    await user.open("/")

    # Should see the crypto position
    await user.should_see("BTC")


async def test_multiple_positions_display(user: User, new_db) -> None:
    """Test that multiple positions display correctly"""
    # Create multiple positions
    positions = [
        PositionCreate(
            asset_symbol="AAPL", asset_type=AssetType.STOCK, shares=Decimal("10.0"), purchase_price=Decimal("150.00")
        ),
        PositionCreate(
            asset_symbol="BTC",
            asset_type=AssetType.CRYPTOCURRENCY,
            shares=Decimal("0.5"),
            purchase_price=Decimal("50000.00"),
        ),
    ]

    for position_data in positions:
        portfolio_service.create_position(position_data)

    await user.open("/")

    # Should see all positions
    await user.should_see("AAPL")
    await user.should_see("BTC")

    # Should see both asset types
    await user.should_see("Stock")

    # Should show 2 total positions
    await user.should_see("2")


async def test_portfolio_value_calculations(user: User, new_db) -> None:
    """Test that portfolio value calculations are displayed"""
    # Create a position
    position_data = PositionCreate(
        asset_symbol="AAPL", asset_type=AssetType.STOCK, shares=Decimal("10.0"), purchase_price=Decimal("150.00")
    )

    portfolio_service.create_position(position_data)

    await user.open("/")

    # Should see portfolio metrics
    await user.should_see("Total Value")
    await user.should_see("Total Cost")
    await user.should_see("Total ROI")


async def test_form_button_functionality(user: User, new_db) -> None:
    """Test that form buttons exist and are functional"""
    await user.open("/")

    # Check that buttons exist
    await user.should_see("Add Position")
    await user.should_see("Clear")

    # Test clicking buttons (they should not crash)
    user.find("Clear").click()
    # Note: We can't easily test the Add Position button without filling the form


# Additional UI smoke tests
async def test_page_header_and_navigation(user: User, new_db) -> None:
    """Test that page header displays correctly"""
    await user.open("/")

    await user.should_see("Portfolio Tracker")


async def test_form_placeholders(user: User, new_db) -> None:
    """Test that form has appropriate placeholders"""
    await user.open("/")

    # Form should have helpful placeholders
    await user.should_see("e.g., AAPL, BTC")


async def test_summary_card_styling(user: User, new_db) -> None:
    """Test that summary card has proper styling and layout"""
    await user.open("/")

    # Summary card should have all key metrics
    await user.should_see("Total Positions")
    await user.should_see("Total Value")
    await user.should_see("Total Cost")
    await user.should_see("Total ROI")
    await user.should_see("P&L")
