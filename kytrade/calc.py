"""Calculations - Easier to test here than in the portfolio"""
import math


def compound_anual_growth_rate(begin_value: float, end_value: float, years: float) -> float:
    """Return the CAGR of given values"""
    # https://www.investopedia.com/terms/c/cagr.asp
    if begin_value == 0 or years == 0:
        return 0
    return ((end_value / begin_value) ** (1 / years) - 1) * 100


def stock_close_average(stocks: list):
    """Return the average close price of a list of stocks"""
    close_prices = [stock.close for stock in stocks]
    return sum(close_prices) / len(stocks)


def stock_close_variance(stocks: list, degrees_of_freedom: int = 1) -> float:
    """Given a list of stock prices, calculate their daily variance"""
    num_values = len(stocks)
    mean = sum([stock.close for stock in stocks]) / num_values
    return sum([(stock.close - mean) ** 2 for stock in stocks]) / (num_values - degrees_of_freedom)


def stocks_close_standard_dev(stocks: list, degrees_of_freedom: int = 1) -> float:
    """Return the standard deviation at close of given stocks"""
    variance = stock_close_variance(stocks, degrees_of_freedom=degrees_of_freedom)
    return math.sqrt(variance)
