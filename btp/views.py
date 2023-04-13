from rest_framework.decorators import api_view
from rest_framework.response import Response
import math
import yfinance as yf
import datetime

def getRate():
    # Define the start and end dates for the data
    years = 10
    start_date = datetime.datetime.now() - datetime.timedelta(days=365*years)
    end_date = datetime.datetime.now()

    # Define the ticker symbol for NIFTY
    ticker_symbol = "^NSEI"

    # Use yfinance to download the data
    data = yf.download(ticker_symbol, start=start_date, end=end_date)

    # Extract the closing prices from the data
    closing_prices = data["Close"]

    rate = closing_prices[-1] / closing_prices[0]
    rate = math.pow(rate,1/years) - 1
    rate = rate * 100
    return rate


@api_view(['GET'])
def btp(request, amount, time):
    result = None
    rate = getRate()
    ci = amount*math.pow((1+rate/100),time)
    return Response({'result': ci, "rate" : rate})
