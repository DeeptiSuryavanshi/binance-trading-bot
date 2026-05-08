# Binance Futures Testnet Trading Bot

A modular, production-quality Python trading bot for the **Binance USDT-M Futures Testnet**.  
Supports MARKET, LIMIT, and STOP\_MARKET orders via a fully interactive CLI.

---

## Table of Contents

1. [Architecture](#architecture)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running the Bot](#running-the-bot)
6. [Order Examples](#order-examples)
7. [Logging](#logging)
8. [Technical Assumptions](#technical-assumptions)
9. [Project Structure](#project-structure)

---

## Architecture

```
┌─────────────────────────────────────────────┐
│                  cli.py                     │  ← UI layer (questionary + rich)
│  questionary prompts → OrderManager calls   │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────▼────────────────────────┐
│             bot/orders.py                   │  ← Business logic
│  market_order / limit_order /               │
│  stop_market_order                          │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────▼────────────────────────┐
│            bot/validators.py                │  ← Input validation (raises ValueError)
└────────────────────┬────────────────────────┘
                     │
┌────────────────────▼────────────────────────┐
│             bot/client.py                   │  ← API layer (python-binance wrapper)
│  BinanceClient  → futures_create_order()    │
│  FUTURES_URL = https://testnet.binancefuture│
│                          .com               │
└─────────────────────────────────────────────┘
```

Each layer has a single responsibility.  The CLI never touches the HTTP client directly.

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | ≥ 3.10 |
| pip | ≥ 23 |
| Binance Futures Testnet account | — |

**Get testnet API keys** at <https://testnet.binancefuture.com> → *Account* → *API Management*.

---

## Installation

```bash
# 1. Clone / unzip the project
cd trading_bot

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Configuration

Copy the example env file and fill in your testnet credentials:

```bash
cp .env.example .env   # or just edit .env directly
```

Edit `.env`:

```dotenv
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
```

> ⚠️  **Never commit real credentials to version control.**  
> The `.env` file is intentionally excluded from any repository via `.gitignore`.

---

## Running the Bot

```bash
# From the trading_bot/ directory (with .venv active)
python cli.py
```

You will see an interactive menu:

```
╭────────────────────────────────────────────╮
│  Binance Futures Testnet Trading Bot       │
│  USDT-M Perpetual Futures · Paper Trading  │
╰────────────────────────────────────────────╯

? What would you like to do?
  ❯ Place a new order
    Exit
```

---

## Order Examples

### MARKET Order (BUY 0.01 BTCUSDT at market price)

```
? Select order type:   MARKET
? Symbol (e.g. BTCUSDT): BTCUSDT
? Side:  BUY
? Quantity: 0.01
```

**Expected rich output:**

```
╭─────────────────── ✅  Order Response ───────────────────╮
│ Field          │ Value                                   │
│ orderId        │ 3492847261                              │
│ symbol         │ BTCUSDT                                 │
│ side           │ BUY                                     │
│ type           │ MARKET                                  │
│ origQty        │ 0.01                                    │
│ status         │ FILLED                                  │
│ executedQty    │ 0.01                                    │
│ avgPrice       │ 67340.50                                │
╰─────────────────────────────────────────────────────────╯
```

---

### LIMIT Order (SELL 0.01 BTCUSDT at 70 000 USDT)

```
? Select order type:   LIMIT
? Symbol:   BTCUSDT
? Side:     SELL
? Quantity: 0.01
? Limit Price (USDT): 70000
```

---

### STOP\_MARKET Order (BUY 0.01 BTCUSDT when price hits 68 000)

```
? Select order type:   STOP_MARKET
? Symbol:     BTCUSDT
? Side:       BUY
? Quantity:   0.01
? Stop Price: 68000
```

---

## Logging

All activity is written to **`trading_bot.log`** in the project root.

Log levels:

| Level | Destination |
|-------|-------------|
| DEBUG | File only |
| INFO  | File + stdout |
| ERROR | File + stdout (with stack trace) |

Sample log entries:

```
2025-06-10 14:22:01 | INFO     | bot.orders | MARKET order | symbol=BTCUSDT side=BUY qty=0.01
2025-06-10 14:22:01 | INFO     | bot.client | Placing futures order | params: {'symbol': 'BTCUSDT', ...}
2025-06-10 14:22:02 | INFO     | bot.client | Order response: {'orderId': 349284726, 'status': 'FILLED', ...}
2025-06-10 14:22:15 | ERROR    | bot.client | BinanceAPIException: code=-1121 msg=Invalid symbol. | ...
Traceback (most recent call last): ...
```

---

## Technical Assumptions

| # | Assumption |
|---|-----------|
| 1 | **Testnet only.** `BinanceClient` sets `testnet=True` *and* explicitly overrides `Client.FUTURES_URL` to `https://testnet.binancefuture.com`. This guarantees all REST calls hit the paper-trading environment even if the `python-binance` library defaults change in a future version. |
| 2 | **USDT-M perpetuals only.** Symbols are validated to end with `USDT`. Coin-margined (COIN-M) contracts are out of scope. |
| 3 | **`python-binance` ≥ 1.0.19.** The `FUTURE_ORDER_TYPE_*` enums are imported from `binance.enums`. If you use an older version, substitute the string literals (`"MARKET"`, `"LIMIT"`, `"STOP_MARKET"`). |
| 4 | **Default `timeInForce` for LIMIT orders is `GTC`** (Good Till Cancelled), which is the most common choice for futures. |
| 5 | **Quantity precision** is not adjusted automatically. Binance enforces step-size rules per symbol. If you receive a `-1111` (precision) error, round your quantity to the allowed decimal places for that symbol. |
| 6 | **No position-mode awareness.** The bot uses the default one-way position mode. If your testnet account is set to hedge mode, you must add a `positionSide` parameter to each order. |

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py          # Package exports: BinanceClient, OrderManager
│   ├── client.py            # BinanceClient — HTTP wrapper (testnet USDT-M)
│   ├── orders.py            # OrderManager — market / limit / stop_market
│   ├── validators.py        # Pure validation functions (raise ValueError)
│   └── logging_config.py   # Centralised logging to trading_bot.log
├── cli.py                   # Interactive CLI (questionary + rich)
├── .env                     # API credentials (git-ignored)
├── requirements.txt         # Pinned dependencies
└── README.md                # This file
```#   b i n a n c e - t r a d i n g - b o t  
 