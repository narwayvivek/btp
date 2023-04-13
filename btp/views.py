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


def getFDrate(time):
    # Fixed deposit interest rates for popular banks in India
    fixed_deposit_interest_rates = {
        "Average Interest Rate": {
            "Regular Citizen": {
                "7 Days to 45 Days": 2.90,
                "46 Days to 179 Days": 3.90,
                "180 Days to 210 Days": 4.40,
                "211 Days to less than 1 Year": 4.40,
                "1 Year to less than 2 Years": 4.90,
                "2 Years to less than 3 Years": 4.90,
                "3 Years to less than 5 Years": 5.40,
                "5 Years and up to 10 Years": 5.40
            },
            "Senior Citizen": {
                "7 Days to 45 Days": 3.40,
                "46 Days to 179 Days": 4.40,
                "180 Days to 210 Days": 4.90,
                "211 Days to less than 1 Year": 4.90,
                "1 Year to less than 2 Years": 5.40,
                "2 Years to less than 3 Years": 5.40,
                "3 Years to less than 5 Years": 5.90,
                "5 Years and up to 10 Years": 5.90
            }
        }
    }
    # time is in years
    if time < 0.2:
        return fixed_deposit_interest_rates["Average Interest Rate"][
            "Regular Citizen"]["7 Days to 45 Days"]
    elif time < 0.5:
        return fixed_deposit_interest_rates["Average Interest Rate"][
            "Regular Citizen"]["46 Days to 179 Days"]
    elif time < 0.58:
        return fixed_deposit_interest_rates["Average Interest Rate"][
            "Regular Citizen"]["180 Days to 210 Days"]
    elif time < 1:
        return fixed_deposit_interest_rates["Average Interest Rate"][
            "Regular Citizen"]["211 Days to less than 1 Year"]
    elif time < 2:
        return fixed_deposit_interest_rates["Average Interest Rate"][
            "Regular Citizen"]["1 Year to less than 2 Years"]
    elif time < 3:
        return fixed_deposit_interest_rates["Average Interest Rate"][
            "Regular Citizen"]["2 Years to less than 3 Years"]
    elif time < 5:
        return fixed_deposit_interest_rates["Average Interest Rate"][
            "Regular Citizen"]["3 Years to less than 5 Years"]
    else:
        return fixed_deposit_interest_rates["Average Interest Rate"][
            "Regular Citizen"]["5 Years and up to 10 Years"]


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
    rate['Savings Account'] = 3.5
    rate['Mutual Funds'] = 10
    rate['Fixed Deposit'] = getFDrate(time)
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
