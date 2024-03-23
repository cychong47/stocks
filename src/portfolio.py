#!/usr/bin/env python

from typing import Dict, List
from rich.table import Table
from rich.console import Console
from rich.style import Style
from operator import attrgetter

# import plotify.graph_objects as go
# from plotly import graph_objs as go
import numpy as np

from stock_price import Stock
from exchange_rate import get_exchange_rate
import warnings

warnings.filterwarnings("ignore", category=FutureWarning, module="yfinance")
import yfinance as yf  # noqa


class InvestmentPerformance:
    def __init__(self, exchange_rate):
        self.total_cost = 0
        self.total_value = 0
        self.profit_loss = 0
        self.exchange_rate = exchange_rate

    def add(self, stock: Stock, earnings: float | int) -> None:
        """Add to a investment

        Args:
            stock (Stock): stock to add
        """

        self.total_cost += stock.purchase_price * stock.amount * self.exchange_rate
        self.total_value += stock.current_price * stock.amount * self.exchange_rate
        self.profit_loss += earnings * self.exchange_rate


class PortfolioPerformance:
    def __init__(self, daily: int):
        self.daily_styling = daily

        self.d2w_exchange_rate = get_exchange_rate()

        kr_investment = InvestmentPerformance(1)
        us_investment = InvestmentPerformance(self.d2w_exchange_rate)

        self.investments = {
            "kr": kr_investment,
            "us": us_investment,
        }

        self.style_red = Style(color="rgb(255,100,100)")
        self.style_blue = Style(color="Blue")

        self.table = Table()
        self.print_header()

    def print_header(self) -> None:
        self.table.add_column("name", justify="left")
        self.table.add_column("amount", justify="right")
        self.table.add_column("inverstment(W)", justify="right")
        self.table.add_column("current(W)", justify="right")
        self.table.add_column("earnings(W)", justify="right")
        self.table.add_column("ratio", justify="right")
        self.table.add_column("purchase", justify="right")
        self.table.add_column("today", justify="right")
        self.table.add_column("daily", justify="right")

    def _get_earnings(self, stock: Stock) -> float | int:
        """Calculate earnings

        Args:
            stock (Stock):

        Returns:
            float|int: earnings
        """

        earnings = (stock.current_price - stock.purchase_price) * stock.amount

        if isinstance(earnings, np.float64):
            try:
                earnings = earnings.astype(int)
            except Exception:
                earnings = 0

        return earnings

    def _get_style(self, stock: Stock) -> Style:
        """Get style for rich.Table row

        Args:
            stock (Stock)

        Returns:
            Style:
        """

        if self.daily_styling:
            return (
                self.style_red
                if stock.current_price >= stock.prev_price
                else self.style_blue
            )
        else:
            return (
                self.style_red
                if stock.current_price >= stock.purchase_price
                else self.style_blue
            )

    def print_investment(self, investment: InvestmentPerformance) -> None:
        """Print investment

        Args:
            investment (Dict):
        """

        self.table.add_section()
        self.table.add_row(
            "",
            "",
            f"{int(investment.total_cost):,}",
            f"{int(investment.total_value):,}",
            f"{int(investment.profit_loss):,}",
            "",
            "",
            "",
            "",
            "",
            # style="on black",
            end_section=True,
        )

    def split_stock_by_country(self, stocks: List) -> Dict:
        """Separate stocks by country

        Args:
            stocks (List): stocks

        Returns:
            Dict
        """

        stock_per_country = {"kr": [], "us": []}

        for stock in stocks:
            if stock.country == "kr":
                stock_per_country["kr"].append(stock)
            else:
                stock_per_country["us"].append(stock)

        stock_per_country["kr"] = sorted(
            stock_per_country["kr"], key=attrgetter("name")
        )
        stock_per_country["us"] = sorted(
            stock_per_country["us"], key=attrgetter("name")
        )

        return stock_per_country

    def add_stock(self, stock: Stock, earnings: float | int) -> None:
        """Add stock to the table

        Args:
            stock (Stock):
            earnings (float | int):
        """

        purchase_price = stock.purchase_price
        current_price = stock.current_price
        prev_price = stock.prev_price
        amount = stock.amount

        exchange_rate = 1 if stock.country == "kr" else self.d2w_exchange_rate

        self.table.add_row(
            stock.name,
            f"{amount}",
            f"{int(purchase_price*amount*exchange_rate):,}",
            f"{int(current_price*amount*exchange_rate):,}",
            f"{int(earnings*exchange_rate):,}",
            f"{current_price/purchase_price*100:5.2f}%",
            f"{purchase_price:>10.2f}",
            f"{current_price:>10.2f}",
            f"{float(current_price - prev_price):>9.2f}",
            f"{float((current_price - prev_price)/prev_price*100):6.2f}%",
            style=self._get_style(stock),
        )

    def process_stock(self, stocks: List) -> None:
        """Process stocks

        Args:
            stocks (List): stocks to process
        """

        stock_per_country = self.split_stock_by_country(stocks)

        for country, country_stock in stock_per_country.items():
            for stock in country_stock:
                earnings = self._get_earnings(stock)

                self.add_stock(stock, earnings)
                self.investments[country].add(stock, earnings)

            self.print_investment(self.investments[country])

    def print(self) -> None:
        console = Console()
        console.print(self.table)
