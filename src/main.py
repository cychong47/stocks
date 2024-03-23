#!/usr/bin/env python

import argparse
import os

from stock_price import StockMarket
from portfolio import PortfolioPerformance


def main(filename: str, daily: bool) -> None:
    """main

    Args:
        filename (str): stock file
        daily (bool): True if color-coding is based on daily changes in stock value
    """

    stock_price = StockMarket(filename)

    my_stocks = stock_price.get_stocks()
    my_agg_stocks = stock_price.get_aggregated_stocks()

    portfolio = PortfolioPerformance(daily)

    portfolio.process_stock(my_agg_stocks)
    portfolio.process_stock(my_stocks)
    portfolio.print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--file",
        default=os.environ.get("STOCK_FILE", "stock.json"),
        help="stock file",
    )
    parser.add_argument(
        "-d",
        "--daily",
        action="store_true",
        default=False,
        help="styling based on daily change",
    )
    args = parser.parse_args()

    main(args.file, args.daily)
