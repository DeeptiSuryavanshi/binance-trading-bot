"""
trading_bot.bot.validators
~~~~~~~~~~~~~~~~~~~~~~~~~~
Pure-function validators for order parameters.
Raises ``ValueError`` with a descriptive message on invalid input.
"""

from __future__ import annotations

from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


# ---------------------------------------------------------------------------
# Public validators
# ---------------------------------------------------------------------------


def validate_symbol(symbol: str) -> str:
    """
    Normalise and validate a trading symbol.

    Rules
    -----
    * Must be a non-empty string.
    * Converted to upper-case.
    * Must end with ``USDT`` (USDT-M perpetual futures).

    Returns
    -------
    str
        The normalised, upper-cased symbol.

    Raises
    ------
    ValueError
        If the symbol is empty or does not end with ``USDT``.
    """
    if not isinstance(symbol, str) or not symbol.strip():
        raise ValueError("Symbol must be a non-empty string.")

    symbol = symbol.strip().upper()

    if not symbol.endswith("USDT"):
        raise ValueError(
            f"Symbol '{symbol}' does not appear to be a USDT-M futures pair. "
            "Expected format: <BASE>USDT  (e.g. BTCUSDT, ETHUSDT)."
        )

    return symbol


def validate_side(side: str) -> str:
    """
    Validate order side.

    Returns
    -------
    str
        Upper-cased side string (``'BUY'`` or ``'SELL'``).

    Raises
    ------
    ValueError
        If *side* is not ``'BUY'`` or ``'SELL'``.
    """
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(
            f"Invalid side '{side}'. Must be one of: {sorted(VALID_SIDES)}."
        )
    return side


def validate_order_type(order_type: str) -> str:
    """
    Validate order type.

    Returns
    -------
    str
        Upper-cased order type string.

    Raises
    ------
    ValueError
        If *order_type* is not in ``VALID_ORDER_TYPES``.
    """
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. "
            f"Must be one of: {sorted(VALID_ORDER_TYPES)}."
        )
    return order_type


def validate_quantity(quantity: float) -> float:
    """
    Validate order quantity.

    Rules
    -----
    * Must be a positive finite number.
    * The Binance Futures testnet enforces minimum notional values; this
      function only guards against obviously invalid inputs.

    Raises
    ------
    ValueError
        If *quantity* is not positive.
    """
    try:
        quantity = float(quantity)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Quantity must be a number, got '{quantity}'.") from exc

    if quantity <= 0:
        raise ValueError(f"Quantity must be > 0, got {quantity}.")

    return quantity


def validate_price(price: float, *, field_name: str = "price") -> float:
    """
    Validate a price or stop-price value.

    Raises
    ------
    ValueError
        If *price* is not positive.
    """
    try:
        price = float(price)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"{field_name} must be a number, got '{price}'."
        ) from exc

    if price <= 0:
        raise ValueError(f"{field_name} must be > 0, got {price}.")

    return price


def validate_limit_order(
    symbol: str,
    side: str,
    quantity: float,
    price: float,
) -> tuple[str, str, float, float]:
    """Convenience wrapper that validates all LIMIT order fields at once."""
    return (
        validate_symbol(symbol),
        validate_side(side),
        validate_quantity(quantity),
        validate_price(price, field_name="price"),
    )


def validate_stop_market_order(
    symbol: str,
    side: str,
    quantity: float,
    stop_price: float,
) -> tuple[str, str, float, float]:
    """Convenience wrapper that validates all STOP_MARKET order fields at once."""
    return (
        validate_symbol(symbol),
        validate_side(side),
        validate_quantity(quantity),
        validate_price(stop_price, field_name="stop_price"),
    )