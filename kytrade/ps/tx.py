"""Portfolio transactions"""
import math

import kytrade.exceptions as exc
from kytrade.data import models
from kytrade.data import db
from kytrade.stock_market import StockMarket
from kytrade.ps.enums import CashOperationAction
from kytrade.ps import portfolio as ps


def modify_cash(portfolio: models.Portfolio, delta: float, subtract: bool = False) -> None:
    """Modify the qty of cash in the portfolio, not allowing negatives"""
    cash = portfolio.data["cash"]
    if subtract:
        delta = -1 * delta
    new_val = cash + delta
    if new_val < 0:
        raise exc.InsufficientFundsError(f"Portfolio cash {new_val} is negative")
    portfolio.data["cash"] = new_val


def deposit(portfolio: models.Portfolio, usd: float) -> None:
    """Deposit funds into the portfolio"""
    ps.log_cash_operation(portfolio, ps.CashOperationAction.DEPOSIT, usd)
    modify_cash(portfolio, usd)


def withdraw(portfolio: models.Portfolio, usd: float) -> None:
    """Withdraw funds from the portfolio"""
    ps.log_cash_operation(portfolio, CashOperationAction.WITHDRAW, usd)
    modify_cash(portfolio, usd, subtract=True)


def add_stock(portfolio: models.Portfolio, symbol: str, qty: int) -> None:
    """Add qty of stock with given symbol to the portfolio"""
    if symbol in portfolio.data["stock_positions"]:
        portfolio.data["stock_positions"][symbol] += qty
    else:
        portfolio.data["stock_positions"][symbol] = qty


def remove_stock(portfolio: models.Portfolio, symbol: str, qty: int) -> None:
    """Remove qty of stock with given symbom from portfolio or raise InsufficientSharesError"""
    if symbol not in portfolio.data["stock_positions"]:
        new_qty = -1 * qty
    else:
        new_qty = portfolio.data["stock_positions"][symbol] - qty
    if new_qty < 0:
        raise exc.InsufficientFundsError(f"Can't have {new_qty} of {symbol} - no shorting!")
    if new_qty == 0:
        del portfolio.data["stock_positions"][symbol]
    portfolio.data["stock_positions"][symbol] = new_qty


def buy_stock(portfolio: models.Portfolio, symbol: str, qty: int, comp: bool = False) -> None:
    """Buy stock in the given portfolio"""
    sm = StockMarket()
    unit_price = sm.get_spot(symbol, portfolio.date).close
    total_price = unit_price * qty
    if comp:
        deposit(portfolio, total_price)
    modify_cash(portfolio, total_price, subtract=True)
    add_stock(portfolio, symbol, qty)
    ps.log_stock_transaction(portfolio, symbol, qty, unit_price, ps.TransactionAction.BUY)


def sell_stock(portfolio: models.Portfolio, symbol: str, qty: int) -> None:
    """Sell stock from the given portfolio"""
    sm = StockMarket()
    unit_price = sm.get_spot(symbol, portfolio.date).close
    total_price = unit_price * qty
    remove_stock(portfolio, symbol, qty)
    modify_cash(portfolio, total_price)
    ps.log_stock_transaction(portfolio, symbol, qty, unit_price, ps.TransactionAction.SELL)


def buy_stock_by_cost(portfolio: models.Portfolio, symbol: str, cost: float) -> None:
    """Buy as many stock as can be afforded at a given cost - no factional shares"""
    sm = StockMarket()
    unit_price = sm.get_spot(symbol, portfolio.date).close
    qty = math.floor(cost / unit_price)
    buy_stock(portfolio, symbol, qty)


def sell_stock_by_cost(portfolio: models.Portfolio, symbol: str, cost: float) -> None:
    """Sell as many shares as needed to earn given cost"""
    sm = StockMarket()
    unit_price = sm.get_spot(symbol, portfolio.date).close
    qty = math.ceil(cost / unit_price)
    sell_stock(portfolio, symbol, qty)
