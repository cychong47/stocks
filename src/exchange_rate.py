#!/usr/bin/env python3

import yfinance as yf


def get_exchange_rate():
    if True:
        df = yf.download("KRW=X", progress=False)
        exchange_rate = df["Close"].iloc[-1]
    else:
        from forex_python.converter import CurrencyRates

        c = CurrencyRates()
        exchange_rate = c.get_rates("USD")["KRW"]

    return exchange_rate
