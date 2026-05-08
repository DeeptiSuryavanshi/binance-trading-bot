"""
trading_bot.bot.orders
~~~~~~~~~~~~~~~~~~~~~~
High-level order helpers that validate inputs, delegate to
:class:`~trading_bot.bot.client.BinanceClient`, and return the raw
Binance response dict.
"""

from __future__ import annotations

from typing import Any, Dict

# pyrefly: ignore [missing-import]
from binance.enums import (
    FUTURE_ORDER_TYPE_LIMIT,
    FUTURE_ORDER_TYPE_MARKET,
    FUTURE_ORDER_TYPE_STOP_MARKET,
    ORDER_TYPE_LIMIT,
    ORDER_TYPE_MARKET,
    TIME_IN_FORCE_GTC,
)

from .client import BinanceClient
from .logging_config import get_logger
from .validators import (
    validate_limit_order,
    validate_quantity,
    validate_side,
    validate_stop_market_order,
    validate_symbol,
)

logger = get_logger(__name__)


class OrderManager:
    """
    Provides named methods for each supported order type.

    All methods validate their inputs via :mod:`~trading_bot.bot.validators`
    before forwarding the call to :class:`~trading_bot.bot.client.BinanceClient`.

    Parameters
    ----------
    client:
        An already-authenticated :class:`BinanceClient` instance.
    """

    def __init__(self, client: BinanceClient) -> None:
        self._client = client

    # ------------------------------------------------------------------
    # MARKET order
    # ------------------------------------------------------------------

    def market_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
    ) -> Dict[str, Any]:
        """
        Place a MARKET order on the USDT-M Futures testnet.

        Parameters
        ----------
        symbol:
            Trading pair, e.g. ``'BTCUSDT'``.
        side:
            ``'BUY'`` or ``'SELL'``.
        quantity:
            Contract quantity (in base asset units).

        Returns
        -------
        dict
            Raw Binance API response.
        """
        symbol = validate_symbol(symbol)
        side = validate_side(side)
        quantity = validate_quantity(quantity)

        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": FUTURE_ORDER_TYPE_MARKET,
            "quantity": quantity,
        }

        logger.info(
            "MARKET order | symbol=%s side=%s qty=%s",
            symbol,
            side,
            quantity,
        )
        return self._client.place_order(**params)

    # ------------------------------------------------------------------
    # LIMIT order
    # ------------------------------------------------------------------

    def limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        time_in_force: str = TIME_IN_FORCE_GTC,
    ) -> Dict[str, Any]:
        """
        Place a LIMIT order on the USDT-M Futures testnet.

        Parameters
        ----------
        symbol:
            Trading pair, e.g. ``'BTCUSDT'``.
        side:
            ``'BUY'`` or ``'SELL'``.
        quantity:
            Contract quantity.
        price:
            Limit price in USDT.
        time_in_force:
            Default ``'GTC'`` (Good Till Cancelled).

        Returns
        -------
        dict
            Raw Binance API response.
        """
        symbol, side, quantity, price = validate_limit_order(
            symbol, side, quantity, price
        )

        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": FUTURE_ORDER_TYPE_LIMIT,
            "quantity": quantity,
            "price": price,
            "timeInForce": time_in_force,
        }

        logger.info(
            "LIMIT order | symbol=%s side=%s qty=%s price=%s tif=%s",
            symbol,
            side,
            quantity,
            price,
            time_in_force,
        )
        return self._client.place_order(**params)

    # ------------------------------------------------------------------
    # STOP_MARKET order  (bonus)
    # ------------------------------------------------------------------

    def stop_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stop_price: float,
    ) -> Dict[str, Any]:
        """
        Place a STOP_MARKET order on the USDT-M Futures testnet.

        A STOP_MARKET order becomes a market order once *stop_price* is
        reached, making it suitable for both stop-loss and stop-entry
        strategies.

        Parameters
        ----------
        symbol:
            Trading pair, e.g. ``'BTCUSDT'``.
        side:
            ``'BUY'`` or ``'SELL'``.
        quantity:
            Contract quantity.
        stop_price:
            Trigger price in USDT.

        Returns
        -------
        dict
            Raw Binance API response.
        """
        symbol, side, quantity, stop_price = validate_stop_market_order(
            symbol, side, quantity, stop_price
        )

        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": FUTURE_ORDER_TYPE_STOP_MARKET,
            "quantity": quantity,
            "stopPrice": stop_price,
        }

        logger.info(
            "STOP_MARKET order | symbol=%s side=%s qty=%s stopPrice=%s",
            symbol,
            side,
            quantity,
            stop_price,
        )
        return self._client.place_order(**params)