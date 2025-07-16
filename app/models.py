from sqlmodel import SQLModel, Field
from datetime import datetime
from decimal import Decimal
from typing import Optional
from enum import Enum


class AssetType(str, Enum):
    STOCK = "stock"
    CRYPTOCURRENCY = "crypto"


# Persistent models (stored in database)
class Position(SQLModel, table=True):
    __tablename__ = "positions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    asset_symbol: str = Field(max_length=20, index=True)
    asset_type: AssetType = Field(default=AssetType.STOCK)
    shares: Decimal = Field(decimal_places=8, max_digits=20)
    purchase_price: Decimal = Field(decimal_places=2, max_digits=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def total_cost(self) -> Decimal:
        """Calculate total cost of the position"""
        return self.shares * self.purchase_price


# Non-persistent schemas (for validation, forms, API requests/responses)
class PositionCreate(SQLModel, table=False):
    asset_symbol: str = Field(max_length=20)
    asset_type: AssetType = Field(default=AssetType.STOCK)
    shares: Decimal = Field(decimal_places=8, max_digits=20, gt=0)
    purchase_price: Decimal = Field(decimal_places=2, max_digits=20, gt=0)


class PositionUpdate(SQLModel, table=False):
    asset_symbol: Optional[str] = Field(default=None, max_length=20)
    asset_type: Optional[AssetType] = Field(default=None)
    shares: Optional[Decimal] = Field(default=None, decimal_places=8, max_digits=20, gt=0)
    purchase_price: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=20, gt=0)


class PositionWithMetrics(SQLModel, table=False):
    """Position with calculated metrics for display"""

    id: Optional[int]
    asset_symbol: str
    asset_type: AssetType
    shares: Decimal
    purchase_price: Decimal
    current_price: Decimal
    current_value: Decimal
    roi_percentage: Decimal
    profit_loss: Decimal
    created_at: datetime
    updated_at: datetime


class PortfolioSummary(SQLModel, table=False):
    """Summary statistics for the entire portfolio"""

    total_positions: int
    total_value: Decimal
    total_cost: Decimal
    total_roi_percentage: Decimal
    total_profit_loss: Decimal
    last_updated: datetime
