from app.database import create_tables
from nicegui import app
import app.portfolio_page


def startup() -> None:
    # this function is called before the first request
    create_tables()
    app.portfolio_page.create()
