from decimal import Decimal
from nicegui import ui
from app.models import AssetType, PositionCreate
from app.portfolio_service import portfolio_service


class PortfolioUI:
    """UI components for portfolio management"""

    def __init__(self):
        self.positions_table = None
        self.summary_card = None
        self.refresh_timer = None

    def create_position_form(self, on_submit_callback=None):
        """Create form for adding new positions"""
        with ui.card().classes("w-full max-w-md p-6 shadow-lg rounded-lg"):
            ui.label("Add New Position").classes("text-xl font-bold mb-6")

            # Asset symbol input
            ui.label("Asset Symbol").classes("text-sm font-medium text-gray-700 mb-1")
            symbol_input = ui.input(placeholder="e.g., AAPL, BTC").classes("w-full mb-4")

            # Asset type selection
            ui.label("Asset Type").classes("text-sm font-medium text-gray-700 mb-1")
            asset_type_select = ui.select(options=["Stock", "Cryptocurrency"], value="Stock").classes("w-full mb-4")

            # Shares input
            ui.label("Number of Shares/Units").classes("text-sm font-medium text-gray-700 mb-1")
            shares_input = ui.number(placeholder="0.00", format="%.8f", min=0.00000001).classes("w-full mb-4")

            # Purchase price input
            ui.label("Purchase Price ($)").classes("text-sm font-medium text-gray-700 mb-1")
            price_input = ui.number(placeholder="0.00", format="%.2f", min=0.01).classes("w-full mb-4")

            # Action buttons
            with ui.row().classes("gap-2 justify-end w-full"):
                ui.button("Cancel", on_click=self.clear_form).classes("px-4 py-2").props("outline")
                ui.button(
                    "Add Position",
                    on_click=lambda: self.add_position(
                        symbol_input.value or "",
                        asset_type_select.value or "Stock",
                        shares_input.value or 0.0,
                        price_input.value or 0.0,
                        on_submit_callback,
                    ),
                ).classes("bg-blue-500 text-white px-4 py-2")

    def add_position(self, symbol: str, asset_type: str, shares: float, price: float, callback=None):
        """Add a new position to the portfolio"""
        try:
            if not symbol or not shares or not price:
                ui.notify("Please fill in all fields", type="negative")
                return

            # Convert string to enum
            asset_type_enum = AssetType.STOCK if asset_type == "Stock" else AssetType.CRYPTOCURRENCY

            position_data = PositionCreate(
                asset_symbol=symbol.strip().upper(),
                asset_type=asset_type_enum,
                shares=Decimal(str(shares)),
                purchase_price=Decimal(str(price)),
            )

            position = portfolio_service.create_position(position_data)
            ui.notify(f"Position {position.asset_symbol} added successfully!", type="positive")

            # Clear form and refresh data
            self.clear_form()
            self.refresh_data()

            if callback:
                callback()

        except Exception as e:
            ui.notify(f"Error adding position: {str(e)}", type="negative")

    def clear_form(self):
        """Clear all form inputs"""
        # This would need to be implemented with specific input references
        pass

    def create_positions_table(self):
        """Create the positions table"""
        positions = portfolio_service.get_positions_with_metrics()

        # Define table columns
        columns = [
            {"name": "symbol", "label": "Symbol", "field": "asset_symbol", "sortable": True},
            {"name": "type", "label": "Type", "field": "asset_type", "sortable": True},
            {"name": "shares", "label": "Shares", "field": "shares", "sortable": True},
            {"name": "purchase_price", "label": "Purchase Price", "field": "purchase_price", "sortable": True},
            {"name": "current_price", "label": "Current Price", "field": "current_price", "sortable": True},
            {"name": "current_value", "label": "Current Value", "field": "current_value", "sortable": True},
            {"name": "roi", "label": "ROI %", "field": "roi_percentage", "sortable": True},
            {"name": "profit_loss", "label": "P&L", "field": "profit_loss", "sortable": True},
            {"name": "actions", "label": "Actions", "field": "actions", "sortable": False},
        ]

        # Convert positions to table rows
        rows = []
        for position in positions:
            rows.append(
                {
                    "id": position.id,
                    "asset_symbol": position.asset_symbol,
                    "asset_type": position.asset_type.title(),
                    "shares": f"{position.shares:.8f}".rstrip("0").rstrip("."),
                    "purchase_price": f"${position.purchase_price:.2f}",
                    "current_price": f"${position.current_price:.2f}",
                    "current_value": f"${position.current_value:.2f}",
                    "roi_percentage": f"{position.roi_percentage:.2f}%",
                    "profit_loss": f"${position.profit_loss:.2f}",
                    "actions": position.id,  # Will be used for action buttons
                }
            )

        if self.positions_table:
            self.positions_table.rows = rows
            self.positions_table.update()
        else:
            self.positions_table = ui.table(columns=columns, rows=rows, row_key="id").classes("w-full")

            # Add action buttons to each row
            self.positions_table.add_slot(
                "body-cell-actions",
                """
                <q-td key="actions" :props="props">
                    <q-btn size="sm" color="primary" icon="edit" @click="$parent.$emit('edit', props.row)" />
                    <q-btn size="sm" color="negative" icon="delete" @click="$parent.$emit('delete', props.row)" />
                </q-td>
            """,
            )

            self.positions_table.on("edit", self.edit_position)
            self.positions_table.on("delete", self.delete_position)

    def edit_position(self, e):
        """Handle position edit"""
        position_id = e.args["id"]
        ui.notify(f"Edit position {position_id} - Feature coming soon!", type="info")

    def delete_position(self, e):
        """Handle position deletion"""
        position_id = e.args["id"]

        async def confirm_delete():
            with ui.dialog() as dialog, ui.card():
                ui.label("Are you sure you want to delete this position?")
                with ui.row():
                    ui.button("Yes", on_click=lambda: dialog.submit("Yes"))
                    ui.button("No", on_click=lambda: dialog.submit("No"))

            result = await dialog
            if result == "Yes":
                if portfolio_service.delete_position(position_id):
                    ui.notify("Position deleted successfully!", type="positive")
                    self.refresh_data()
                else:
                    ui.notify("Error deleting position", type="negative")

        ui.run_javascript(f"""
            (async () => {{
                const confirmed = confirm('Are you sure you want to delete this position?');
                if (confirmed) {{
                    await fetch('/api/delete-position/{position_id}', {{method: 'DELETE'}});
                    window.location.reload();
                }}
            }})();
        """)

    def create_summary_card(self):
        """Create portfolio summary card"""
        summary = portfolio_service.get_portfolio_summary()

        with ui.card().classes(
            "w-full p-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg rounded-lg"
        ):
            ui.label("Portfolio Summary").classes("text-2xl font-bold mb-4")

            with ui.row().classes("gap-8 w-full"):
                # Total positions
                with ui.column().classes("text-center"):
                    ui.label(str(summary.total_positions)).classes("text-3xl font-bold")
                    ui.label("Total Positions").classes("text-sm opacity-90")

                # Total value
                with ui.column().classes("text-center"):
                    ui.label(f"${summary.total_value:,.2f}").classes("text-3xl font-bold")
                    ui.label("Total Value").classes("text-sm opacity-90")

                # Total cost
                with ui.column().classes("text-center"):
                    ui.label(f"${summary.total_cost:,.2f}").classes("text-3xl font-bold")
                    ui.label("Total Cost").classes("text-sm opacity-90")

                # Total ROI
                with ui.column().classes("text-center"):
                    roi_color = "text-green-300" if summary.total_roi_percentage >= 0 else "text-red-300"
                    ui.label(f"{summary.total_roi_percentage:,.2f}%").classes(f"text-3xl font-bold {roi_color}")
                    ui.label("Total ROI").classes("text-sm opacity-90")

                # Profit/Loss
                with ui.column().classes("text-center"):
                    pl_color = "text-green-300" if summary.total_profit_loss >= 0 else "text-red-300"
                    ui.label(f"${summary.total_profit_loss:,.2f}").classes(f"text-3xl font-bold {pl_color}")
                    ui.label("P&L").classes("text-sm opacity-90")

    def refresh_data(self):
        """Refresh all data in the UI"""
        if self.positions_table:
            self.create_positions_table()
        if self.summary_card:
            self.create_summary_card()

    def create_refresh_button(self):
        """Create manual refresh button"""
        ui.button("Refresh Data", on_click=self.refresh_data).classes(
            "bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
        )


# Global UI instance
portfolio_ui = PortfolioUI()
