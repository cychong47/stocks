#!/usr/bin/env python3

import json
import numpy as np
from typing import List
from pydantic import BaseModel
from pandas.core.series import Series

import warnings

warnings.filterwarnings("ignore", category=FutureWarning, module="yfinance")
import yfinance as yf  # noqa


class Stock(BaseModel):
    code: str
    name: str
    country: str
    purchase_price: float = 0.0
    amount: int = 0
    current_price: float = 0.0
    prev_price: float = 0.0

    # total cost to purchase stocks
    total_price: float = 0.0


class StockMarket:
    def __init__(self, filename: str):
        self.ticker_symbols = []
        self.my_stocks = []
        self.filename = filename

    def collect_tickers(self) -> None:
        """Collect tickers"""

        with open(self.filename, "r") as file:
            self.stock_file = json.load(file)

        stock_list = [s["name"] for s in self.stock_file["stocks"]]
        stock_list = list(set(stock_list))
        for stock in stock_list:
            if ticker := self.get_ticker_symbol_by_name(stock):
                if country := self.get_market_country(ticker):
                    self.ticker_symbols.append(
                        Stock(code=ticker, name=stock, country=country)
                    )
                else:
                    print(f"country for {stock} is not found")
            else:
                print(f"Code not find ticker for {stock}")

    def get_stocks(self) -> List:
        close_prices = self.get_stock_prices()

        for stock in self.stock_file["stocks"]:
            ticker_symbol = self.get_ticker_symbol_by_name(stock["name"])
            self.my_stocks.append(
                Stock(
                    code=ticker_symbol,
                    name=stock["name"],
                    country=self.get_market_country(ticker_symbol),
                    purchase_price=stock["purchase_price"],
                    amount=stock["amount"],
                    current_price=self.get_close_price(close_prices[ticker_symbol]),
                    prev_price=self.get_prev_price(close_prices[ticker_symbol]),
                )
            )

        return self.my_stocks

    def get_aggregated_stocks(self) -> List:
        """Get an aggregated stocks"""

        close_prices = self.get_stock_prices()

        my_agg_stocks = {}
        for stock in self.stock_file["stocks"]:
            name = stock["name"]
            ticker_symbol = self.get_ticker_symbol_by_name(name)

            if stock["name"] in my_agg_stocks:
                my_agg_stocks[name].amount += stock["amount"]
                my_agg_stocks[name].purchase_price += stock["purchase_price"]
                my_agg_stocks[name].total_price += (
                    stock["purchase_price"] * stock["amount"]
                )
            else:
                my_agg_stocks[name] = Stock(
                    code=ticker_symbol,
                    name=stock["name"],
                    country=self.get_market_country(ticker_symbol),
                    purchase_price=stock["purchase_price"],
                    amount=stock["amount"],
                    current_price=self.get_close_price(close_prices[ticker_symbol]),
                    prev_price=self.get_prev_price(close_prices[ticker_symbol]),
                    total_price=stock["purchase_price"] * stock["amount"],
                )

        for name, stock in my_agg_stocks.items():
            stock.purchase_price = stock.total_price / stock.amount

        return [stock for stock in my_agg_stocks.values()]

    def get_ticker_symbols(self) -> List:
        return self.ticker_symbols

    def get_ticker_symbol_by_name(self, name: str) -> str:
        return self.stock_file["ticker"].get(name)

    def get_market_country(self, code: str) -> str:
        return "kr" if ".KS" in code or ".KQ" in code else "us"

    def get_stock_prices(self) -> int | float:
        """Get stock price for the given tickers

        To get a price of a specific date
        data = yf.download("AAPL", "2023-08-01", "2023-08-31")
        """

        self.collect_tickers()

        ticker_symbols = [s.code for s in self.ticker_symbols]

        stock_price = yf.download(tickers=ticker_symbols, period="5d", progress=False)

        return stock_price["Close"]

    def pick_a_price(self, prices, close_price=True) -> float | int:
        """Pick a stock price

        Args:
            prices (_type_): _description_
            close_price (bool, optional): if tru_description_. Defaults to True.
                # index -1: lastest close price
                # index -2: close price of a day before

        Returns:
            stock price (float or int)
        """
        index = -1 if close_price else -2

        price = prices.iloc[index]

        # if stock prices is not available due to holiday or something else,
        # then get the prices of a day before
        # if np.isnan(prices):
        if np.isnan(price):
            print("check again")
            price = prices.iloc[index - 1]

        return price.astype(float) if isinstance(price, np.float64) else price

    def get_prev_price(self, price: Series) -> float | int:
        return self.pick_a_price(price, close_price=False)

    def get_close_price(self, price: Series) -> float | int:
        return self.pick_a_price(price, close_price=True)
