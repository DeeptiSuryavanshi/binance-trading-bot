"""
trading_bot.bot.client
~~~~~~~~~~~~~~~~~~~~~~
Thin wrapper around ``python-binance`` targeting the Binance Futures
*Testnet* (USDT-M) endpoint.

Testnet REST base URL : https://testnet.binancefuture.com
"""

from __future__ import annotations

import os
from typing import Any, Dict

import requests
# pyrefly: ignore [missing-import]
from binance.client import Client
# pyrefly: ignore [missing-import]
from binance.exceptions import BinanceAPIException

from .logging_config import get_logger

logger = get_logger(__name__)

# The python-binance library accepts a custom futures base URL via the
# FUTURES_URL class attribute on the Client instance.
FUTURES_TESTNET_URL = "https://testnet.binancefuture.com"


class BinanceClient:
    """
    Authenticated Binance Futures Testnet client.

    The underlying :class:`binance.client.Client` is initialised with
    ``testnet=True``.  Additionally, the futures REST base URL is
    explicitly overridden to ``https://testnet.binancefuture.com`` so that
    every futures API call targets the paper-trading environment.

    Parameters
    ----------
    api_key:
        Binance Testnet API key.  Falls back to the ``BINANCE_API_KEY``
        environment variable when not supplied.
    api_secret:
        Binance Testnet API secret.  Falls back to ``BINANCE_API_SECRET``.

    Raises
    ------
    EnvironmentError
        If neither the constructor arguments nor the environment variables
        supply valid credentials.
    """

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
    ) -> None:
        _key = api_key or os.getenv("BINANCE_API_KEY", "")
        _secret = api_secret or os.getenv("BINANCE_API_SECRET", "")

        if not _key or not _secret:
            raise EnvironmentError(
                "Binance API credentials are missing. "
                "Set BINANCE_API_KEY and BINANCE_API_SECRET in your .env file."
            )

        logger.info("Initialising BinanceClient (testnet=True, USDT-M futures).")

        self._client: Client = Client(
            api_key=_key,
            api_secret=_secret,
            testnet=True,
        )

        # Override the futures REST base so all futures calls hit the testnet.
        self._client.FUTURES_URL = FUTURES_TESTNET_URL
        logger.debug("Futures base URL set to: %s", FUTURES_TESTNET_URL)

    # ------------------------------------------------------------------
    # Low-level order placement
    # ------------------------------------------------------------------

    def place_order(self, **params: Any) -> Dict[str, Any]:
        """
        Forward a futures order to Binance and return the raw response dict.

        All ``**params`` are passed verbatim to
        :meth:`binance.client.Client.futures_create_order` after being
        logged for audit purposes.

        Parameters
        ----------
        **params:
            Any keyword arguments accepted by ``futures_create_order``.
            Typical keys: ``symbol``, ``side``, ``type``, ``quantity``,
            ``price``, ``stopPrice``, ``timeInForce``.

        Returns
        -------
        dict
            The full JSON response from Binance.

        Raises
        ------
        BinanceAPIException
            On any API-level error (e.g. insufficient margin, invalid
            symbol, duplicate ``clientOrderId``).
        requests.exceptions.ReadTimeout
            When the HTTP request times out.
        """
        logger.info("Placing futures order | params: %s", params)

        try:
            response: Dict[str, Any] = self._client.futures_create_order(**params)
            logger.info("Order response: %s", response)
            return response

        except BinanceAPIException as exc:
            logger.error(
                "BinanceAPIException: code=%s msg=%s | params=%s",
                exc.code,
                exc.message,
                params,
                exc_info=True,
            )
            raise

        except requests.exceptions.ReadTimeout as exc:
            logger.error(
                "ReadTimeout while placing order | params=%s",
                params,
                exc_info=True,
            )
            raise

    # ------------------------------------------------------------------
    # Convenience getters (useful for CLI / validation)
    # ------------------------------------------------------------------

    def get_account_info(self) -> Dict[str, Any]:
        """Return futures account information from the testnet."""
        logger.info("Fetching futures account info.")
        try:
            info: Dict[str, Any] = self._client.futures_account()
            logger.debug("Account info: %s", info)
            return info
        except BinanceAPIException as exc:
            logger.error("Failed to fetch account info: %s", exc, exc_info=True)
            raise

    def get_symbol_info(self, symbol: str) -> Dict[str, Any] | None:
        """
        Return exchange-info for *symbol* from the futures testnet, or
        ``None`` if the symbol is not listed.
        """
        logger.info("Fetching symbol info for: %s", symbol)
        try:
            exchange_info = self._client.futures_exchange_info()
            for item in exchange_info.get("symbols", []):
                if item.get("symbol") == symbol:
                    return item
            return None
        except BinanceAPIException as exc:
            logger.error("Failed to fetch exchange info: %s", exc, exc_info=True)
            raise