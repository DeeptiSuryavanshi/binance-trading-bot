"""
trading_bot.cli
~~~~~~~~~~~~~~~
Interactive CLI entry point.

Uses ``questionary`` for menus / text prompts and ``rich`` to render
the Binance API response as a formatted table.

Run:
    python -m trading_bot.cli
or:
    python trading_bot/cli.py
"""

from __future__ import annotations

import sys
from typing import Any, Dict

# pyrefly: ignore [missing-import]
import questionary
import requests
# pyrefly: ignore [missing-import]
from binance.exceptions import BinanceAPIException
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from rich.console import Console
# pyrefly: ignore [missing-import]
from rich.panel import Panel
# pyrefly: ignore [missing-import]
from rich.table import Table
# pyrefly: ignore [missing-import]
from rich import box

from bot.client import BinanceClient
from bot.logging_config import get_logger
from bot.orders import OrderManager

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

load_dotenv()  # load .env before anything touches os.getenv
logger = get_logger(__name__)
console = Console()

# ---------------------------------------------------------------------------
# Rich helpers
# ---------------------------------------------------------------------------

ORDER_TYPE_CHOICES = ["MARKET", "LIMIT", "STOP_MARKET"]
SIDE_CHOICES = ["BUY", "SELL"]


def _render_response(response: Dict[str, Any]) -> None:
    """Render the Binance order response as a two-column Rich table."""
    table = Table(
        title="✅  Order Response",
        box=box.ROUNDED,
        header_style="bold cyan",
        show_lines=True,
        expand=False,
    )
    table.add_column("Field", style="bold yellow", no_wrap=True)
    table.add_column("Value", style="white")

    priority_keys = [
        "orderId",
        "symbol",
        "side",
        "type",
        "origQty",
        "price",
        "stopPrice",
        "status",
        "timeInForce",
        "executedQty",
        "avgPrice",
        "clientOrderId",
        "updateTime",
    ]

    # Show priority keys first (in order), then any remaining keys.
    shown: set[str] = set()
    for key in priority_keys:
        if key in response:
            table.add_row(key, str(response[key]))
            shown.add(key)

    for key, value in response.items():
        if key not in shown:
            table.add_row(key, str(value))

    console.print()
    console.print(table)
    console.print()


def _prompt_float(message: str) -> float:
    """Prompt the user for a float value; re-prompt on invalid input."""
    while True:
        raw = questionary.text(message).ask()
        if raw is None:
            _abort()
        try:
            return float(raw)
        except ValueError:
            console.print(f"[red]⚠  '{raw}' is not a valid number. Try again.[/red]")


def _abort() -> None:
    console.print("[yellow]Aborted.[/yellow]")
    sys.exit(0)


# ---------------------------------------------------------------------------
# Order-type flows
# ---------------------------------------------------------------------------


def _handle_market(manager: OrderManager) -> Dict[str, Any]:
    symbol: str | None = questionary.text(
        "Symbol (e.g. BTCUSDT):", validate=lambda v: bool(v.strip()) or "Cannot be empty."
    ).ask()
    if symbol is None:
        _abort()

    side: str | None = questionary.select("Side:", choices=SIDE_CHOICES).ask()
    if side is None:
        _abort()

    quantity = _prompt_float("Quantity:")
    return manager.market_order(symbol=symbol, side=side, quantity=quantity)


def _handle_limit(manager: OrderManager) -> Dict[str, Any]:
    symbol: str | None = questionary.text(
        "Symbol (e.g. BTCUSDT):", validate=lambda v: bool(v.strip()) or "Cannot be empty."
    ).ask()
    if symbol is None:
        _abort()

    side: str | None = questionary.select("Side:", choices=SIDE_CHOICES).ask()
    if side is None:
        _abort()

    quantity = _prompt_float("Quantity:")
    price = _prompt_float("Limit Price (USDT):")
    return manager.limit_order(symbol=symbol, side=side, quantity=quantity, price=price)


def _handle_stop_market(manager: OrderManager) -> Dict[str, Any]:
    symbol: str | None = questionary.text(
        "Symbol (e.g. BTCUSDT):", validate=lambda v: bool(v.strip()) or "Cannot be empty."
    ).ask()
    if symbol is None:
        _abort()

    side: str | None = questionary.select("Side:", choices=SIDE_CHOICES).ask()
    if side is None:
        _abort()

    quantity = _prompt_float("Quantity:")
    stop_price = _prompt_float("Stop Price (USDT):")
    return manager.stop_market_order(
        symbol=symbol, side=side, quantity=quantity, stop_price=stop_price
    )


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


def main() -> None:
    console.print(
        Panel.fit(
            "[bold cyan]Binance Futures Testnet Trading Bot[/bold cyan]\n"
            "[dim]USDT-M Perpetual Futures  ·  Paper Trading Only[/dim]",
            border_style="cyan",
        )
    )

    # --- initialise client ---
    try:
        client = BinanceClient()
        manager = OrderManager(client)
        logger.info("BinanceClient initialised successfully.")
    except EnvironmentError as exc:
        console.print(f"[bold red]Configuration error:[/bold red] {exc}")
        sys.exit(1)

    # --- main menu loop ---
    while True:
        action: str | None = questionary.select(
            "What would you like to do?",
            choices=[
                "Place a new order",
                "Exit",
            ],
        ).ask()

        if action is None or action == "Exit":
            console.print("[cyan]Goodbye.[/cyan]")
            break

        # --- order type selection ---
        order_type: str | None = questionary.select(
            "Select order type:",
            choices=ORDER_TYPE_CHOICES,
        ).ask()

        if order_type is None:
            continue

        try:
            if order_type == "MARKET":
                response = _handle_market(manager)
            elif order_type == "LIMIT":
                response = _handle_limit(manager)
            else:  # STOP_MARKET
                response = _handle_stop_market(manager)

            _render_response(response)

        except ValueError as exc:
            console.print(f"\n[bold red]Validation error:[/bold red] {exc}\n")
            logger.warning("Validation error: %s", exc)

        except BinanceAPIException as exc:
            console.print(
                f"\n[bold red]Binance API error [code {exc.code}]:[/bold red] {exc.message}\n"
            )
            logger.error("BinanceAPIException: %s", exc, exc_info=True)

        except requests.exceptions.ReadTimeout:
            console.print(
                "\n[bold red]Network timeout:[/bold red] "
                "The request to Binance timed out. Check your connection.\n"
            )
            logger.error("ReadTimeout", exc_info=True)

        except Exception as exc:  # noqa: BLE001
            console.print(f"\n[bold red]Unexpected error:[/bold red] {exc}\n")
            logger.error("Unexpected error: %s", exc, exc_info=True)


if __name__ == "__main__":
    main()