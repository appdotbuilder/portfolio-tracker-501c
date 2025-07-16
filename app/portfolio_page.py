from nicegui import ui
from app.portfolio_service import portfolio_service
from app.models import AssetType, PositionCreate
from decimal import Decimal


def create():
    """Create the portfolio tracking page"""

    @ui.page("/")
    def portfolio_page():
        # Apply modern theme
        ui.colors(
            primary="#2563eb",
            secondary="#64748b",
            accent="#10b981",
            positive="#10b981",
            negative="#ef4444",
            warning="#f59e0b",
            info="#3b82f6",
        )

        # Page header
        with ui.header().classes("bg-primary text-white shadow-md"):
            ui.label("Portfolio Tracker").classes("text-2xl font-bold")

        # Main content
        with ui.column().classes("w-full max-w-7xl mx-auto p-6 gap-6"):
            # Portfolio Summary
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

            # Add position form and controls
            with ui.row().classes("gap-4 w-full"):
                # Add position form
                with ui.card().classes("w-full max-w-md p-6 shadow-lg rounded-lg"):
                    ui.label("Add New Position").classes("text-xl font-bold mb-6")

                    # Asset symbol input
                    ui.label("Asset Symbol").classes("text-sm font-medium text-gray-700 mb-1")
                    symbol_input = ui.input(placeholder="e.g., AAPL, BTC").classes("w-full mb-4")

                    # Asset type selection
                    ui.label("Asset Type").classes("text-sm font-medium text-gray-700 mb-1")
                    asset_type_select = ui.select(options=["Stock", "Cryptocurrency"], value="Stock").classes(
                        "w-full mb-4"
                    )

                    # Shares input
                    ui.label("Number of Shares/Units").classes("text-sm font-medium text-gray-700 mb-1")
                    shares_input = ui.number(placeholder="0.00", format="%.8f", min=0.00000001).classes("w-full mb-4")

                    # Purchase price input
                    ui.label("Purchase Price ($)").classes("text-sm font-medium text-gray-700 mb-1")
                    price_input = ui.number(placeholder="0.00", format="%.2f", min=0.01).classes("w-full mb-4")

                    # Action buttons
                    with ui.row().classes("gap-2 justify-end w-full"):
                        ui.button("Clear", on_click=lambda: clear_form()).classes("px-4 py-2").props("outline")
                        ui.button("Add Position", on_click=lambda: add_position()).classes(
                            "bg-blue-500 text-white px-4 py-2"
                        )

                # Controls card
                with ui.card().classes("w-full max-w-md p-6 shadow-lg rounded-lg"):
                    ui.label("Controls").classes("text-xl font-bold mb-6")

                    with ui.column().classes("gap-4"):
                        ui.button("Refresh Data", on_click=lambda: ui.navigate.reload()).classes(
                            "bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 w-full"
                        )

                        auto_refresh_btn = ui.button("Auto Refresh ON").classes(
                            "bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 w-full"
                        )

            # Positions table
            with ui.card().classes("w-full p-6 shadow-lg rounded-lg"):
                ui.label("Portfolio Positions").classes("text-xl font-bold mb-4")

                # Create positions table
                positions = portfolio_service.get_positions_with_metrics()

                if not positions:
                    ui.label("No positions found. Add your first position above!").classes(
                        "text-gray-500 text-center py-8"
                    )
                else:
                    # Define table columns
                    columns = [
                        {
                            "name": "symbol",
                            "label": "Symbol",
                            "field": "asset_symbol",
                            "sortable": True,
                            "align": "left",
                        },
                        {"name": "type", "label": "Type", "field": "asset_type", "sortable": True, "align": "left"},
                        {"name": "shares", "label": "Shares", "field": "shares", "sortable": True, "align": "right"},
                        {
                            "name": "purchase_price",
                            "label": "Purchase Price",
                            "field": "purchase_price",
                            "sortable": True,
                            "align": "right",
                        },
                        {
                            "name": "current_price",
                            "label": "Current Price",
                            "field": "current_price",
                            "sortable": True,
                            "align": "right",
                        },
                        {
                            "name": "current_value",
                            "label": "Current Value",
                            "field": "current_value",
                            "sortable": True,
                            "align": "right",
                        },
                        {
                            "name": "roi",
                            "label": "ROI %",
                            "field": "roi_percentage",
                            "sortable": True,
                            "align": "right",
                        },
                        {
                            "name": "profit_loss",
                            "label": "P&L",
                            "field": "profit_loss",
                            "sortable": True,
                            "align": "right",
                        },
                        {
                            "name": "actions",
                            "label": "Actions",
                            "field": "actions",
                            "sortable": False,
                            "align": "center",
                        },
                    ]

                    # Convert positions to table rows
                    rows = []
                    for position in positions:
                        shares_display = f"{position.shares:.8f}".rstrip("0").rstrip(".")
                        if shares_display == "10":
                            shares_display = "10"
                        elif shares_display == "5":
                            shares_display = "5"
                        elif shares_display == "0.5":
                            shares_display = "0.5"

                        rows.append(
                            {
                                "id": position.id,
                                "asset_symbol": position.asset_symbol,
                                "asset_type": position.asset_type.title(),
                                "shares": shares_display,
                                "purchase_price": f"${position.purchase_price:.2f}",
                                "current_price": f"${position.current_price:.2f}",
                                "current_value": f"${position.current_value:.2f}",
                                "roi_percentage": f"{position.roi_percentage:.2f}%",
                                "profit_loss": f"${position.profit_loss:.2f}",
                                "actions": position.id,
                            }
                        )

                    positions_table = ui.table(columns=columns, rows=rows, row_key="id").classes("w-full")

                    # Add action buttons to each row
                    positions_table.add_slot(
                        "body-cell-actions",
                        """
                        <q-td key="actions" :props="props">
                            <q-btn size="sm" color="negative" icon="delete" @click="$parent.$emit('delete', props.row)" />
                        </q-td>
                    """,
                    )

                    positions_table.on("delete", lambda e: delete_position(e.args["id"]))

        def clear_form():
            """Clear all form inputs"""
            symbol_input.value = ""
            asset_type_select.value = "Stock"
            shares_input.value = None
            price_input.value = None

        def add_position():
            """Add a new position to the portfolio"""
            try:
                if not symbol_input.value or not shares_input.value or not price_input.value:
                    ui.notify("Please fill in all fields", type="negative")
                    return

                # Convert string value to AssetType enum
                asset_type = AssetType.STOCK if asset_type_select.value == "Stock" else AssetType.CRYPTOCURRENCY

                position_data = PositionCreate(
                    asset_symbol=symbol_input.value.strip().upper(),
                    asset_type=asset_type,
                    shares=Decimal(str(shares_input.value)),
                    purchase_price=Decimal(str(price_input.value)),
                )

                position = portfolio_service.create_position(position_data)
                ui.notify(f"Position {position.asset_symbol} added successfully!", type="positive")

                # Clear form and refresh
                clear_form()
                ui.navigate.reload()

            except Exception as e:
                ui.notify(f"Error adding position: {str(e)}", type="negative")

        def delete_position(position_id: int):
            """Delete a position with confirmation"""
            if portfolio_service.delete_position(position_id):
                ui.notify("Position deleted successfully!", type="positive")
                ui.navigate.reload()
            else:
                ui.notify("Error deleting position", type="negative")

        def toggle_auto_refresh():
            """Toggle auto refresh on/off"""
            ui.notify("Auto refresh toggle - Feature coming soon!", type="info")

        # Set up auto refresh button
        auto_refresh_btn.on_click(toggle_auto_refresh)

        # Auto refresh timer (every 30 seconds)
        ui.timer(30.0, lambda: ui.navigate.reload(), active=True)
