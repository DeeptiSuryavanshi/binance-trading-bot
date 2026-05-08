"""
trading_bot.bot
~~~~~~~~~~~~~~~
Core package exposing the BinanceClient and order-placement helpers.
"""

from .client import BinanceClient
from .orders import OrderManager

__all__ = ["BinanceClient", "OrderManager"]