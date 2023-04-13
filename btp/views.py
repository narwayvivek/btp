from rest_framework.decorators import api_view
from rest_framework.response import Response
import math
import yfinance as yf
import datetime


def getRateonSocks(ticker_symbol):
    # Define the start and end dates for the data
    years = 10
    start_date = datetime.datetime.now() - datetime.timedelta(days=365 * years)
    end_date = datetime.datetime.now()

    # Use yfinance to download the data
    data = yf.download(ticker_symbol, start=start_date, end=end_date)

    # Extract the closing prices from the data
    closing_prices = data["Close"]

    rate = closing_prices[-1] / closing_prices[0]
    rate = math.pow(rate, 1 / years) - 1
    rate = rate * 100
    return rate


def calculateCompoundInterest(amount, rate, time):
    ci = amount * math.pow((1 + rate / 100), time)
    return ci


@api_view(['GET'])
def finCal(request, amount, time):
    financialInstruments = [
        'Savings Account',
        'Fixed Deposit',
        'Mutual Funds',
        'Nifty 50',
        'Bank Nifty',
        'Government Bonds',
        'Corporate Bonds',
        'Gold',
        'Silver',
    ]
    ticker_symbol = {}
    ticker_symbol['Nifty 50'] = '^NSEI'  # NIFTY 50
    ticker_symbol['Bank Nifty'] = '^NSEBANK'  # BANK NIFTY
    ticker_symbol['Gold'] = 'GC=F'  # Gold
    ticker_symbol['Silver'] = 'SI=F'  # Silver
    ticker_symbol['Government Bonds'] = '^TNX'  # 10 Year Treasury Note
    ticker_symbol['Corporate Bonds'] = '^TYX'  # 10 Year Treasury Note
    rate = {}
    for i in ticker_symbol:
        rate[i] = getRateonSocks(ticker_symbol[i])
    ci = {}
    for i in rate:
        ci[i] = calculateCompoundInterest(amount, rate[i], time)

    response_array = []
    for i in ci:
        response_array.append({
            "Instrument Name": i,
            "Rate": rate[i],
            "Maturing Amount": ci[i]
        })
    # json response with
    # {
    #     "Amount Invested": amount,
    #     "Time": time,
    #     { [
    #         "Instrument Name": "Saving Account",
    #         "Rate": rate,
    #         "Maturing Amount": ci],
    #         [
    #         "Instrument Name": "Fixed Deposit",
    #         "Rate": rate,
    #         "Maturing Amount": ci],

    #     }
    # }

    response = {
        "Amount Invested": amount,
        "Time": time,
        "Financial Instruments": response_array
    }

    return Response(response)
