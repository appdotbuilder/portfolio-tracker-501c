from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from sqlmodel import select
from app.database import get_session
from app.models import Position, PositionCreate, PositionUpdate, PositionWithMetrics, PortfolioSummary
from app.price_service import price_service


class PortfolioService:
    """Service for managing portfolio positions and calculations"""

    def create_position(self, position_data: PositionCreate) -> Position:
        """Create a new position in the portfolio"""
        with get_session() as session:
            position = Position(
                asset_symbol=position_data.asset_symbol.upper(),
                asset_type=position_data.asset_type,
                shares=position_data.shares,
                purchase_price=position_data.purchase_price,
            )
            session.add(position)
            session.commit()
            session.refresh(position)
            return position

    def get_position(self, position_id: int) -> Optional[Position]:
        """Get a position by ID"""
        with get_session() as session:
            return session.get(Position, position_id)

    def get_all_positions(self) -> List[Position]:
        """Get all positions in the portfolio"""
        with get_session() as session:
            statement = select(Position)
            return list(session.exec(statement))

    def update_position(self, position_id: int, position_data: PositionUpdate) -> Optional[Position]:
        """Update an existing position"""
        with get_session() as session:
            position = session.get(Position, position_id)
            if position is None:
                return None

            # Update fields that are not None
            if position_data.asset_symbol is not None:
                position.asset_symbol = position_data.asset_symbol.upper()
            if position_data.asset_type is not None:
                position.asset_type = position_data.asset_type
            if position_data.shares is not None:
                position.shares = position_data.shares
            if position_data.purchase_price is not None:
                position.purchase_price = position_data.purchase_price

            position.updated_at = datetime.utcnow()
            session.commit()
            session.refresh(position)
            return position

    def delete_position(self, position_id: int) -> bool:
        """Delete a position by ID"""
        with get_session() as session:
            position = session.get(Position, position_id)
            if position is None:
                return False

            session.delete(position)
            session.commit()
            return True

    def get_positions_with_metrics(self) -> List[PositionWithMetrics]:
        """Get all positions with calculated metrics (current price, ROI, etc.)"""
        positions = self.get_all_positions()
        if not positions:
            return []

        # Get current prices for all positions
        symbols = [(pos.asset_symbol, pos.asset_type) for pos in positions]
        current_prices = price_service.get_multiple_prices(symbols)

        positions_with_metrics = []
        for position in positions:
            current_price = current_prices.get(position.asset_symbol)
            if current_price is None:
                current_price = Decimal("0")

            current_value = Decimal(str(position.shares)) * current_price
            total_cost = Decimal(str(position.shares)) * Decimal(str(position.purchase_price))
            profit_loss = current_value - total_cost

            # Calculate ROI percentage
            roi_percentage = Decimal("0")
            if total_cost > 0:
                roi_percentage = (profit_loss / total_cost) * Decimal("100")

            position_with_metrics = PositionWithMetrics(
                id=position.id,
                asset_symbol=position.asset_symbol,
                asset_type=position.asset_type,
                shares=position.shares,
                purchase_price=position.purchase_price,
                current_price=current_price,
                current_value=current_value,
                roi_percentage=roi_percentage,
                profit_loss=profit_loss,
                created_at=position.created_at,
                updated_at=position.updated_at,
            )
            positions_with_metrics.append(position_with_metrics)

        return positions_with_metrics

    def get_portfolio_summary(self) -> PortfolioSummary:
        """Get portfolio summary with total value, ROI, etc."""
        positions = self.get_positions_with_metrics()

        if not positions:
            return PortfolioSummary(
                total_positions=0,
                total_value=Decimal("0"),
                total_cost=Decimal("0"),
                total_roi_percentage=Decimal("0"),
                total_profit_loss=Decimal("0"),
                last_updated=datetime.utcnow(),
            )

        total_value = sum(pos.current_value for pos in positions)
        total_cost = sum(Decimal(str(pos.shares)) * Decimal(str(pos.purchase_price)) for pos in positions)
        total_profit_loss = Decimal(str(total_value)) - Decimal(str(total_cost))

        total_roi_percentage = Decimal("0")
        if total_cost > 0:
            total_roi_percentage = (total_profit_loss / total_cost) * Decimal("100")

        return PortfolioSummary(
            total_positions=len(positions),
            total_value=Decimal(str(total_value)) if total_value else Decimal("0"),
            total_cost=Decimal(str(total_cost)) if total_cost else Decimal("0"),
            total_roi_percentage=total_roi_percentage,
            total_profit_loss=Decimal(str(total_profit_loss)) if total_profit_loss else Decimal("0"),
            last_updated=datetime.utcnow(),
        )


# Global portfolio service instance
portfolio_service = PortfolioService()
