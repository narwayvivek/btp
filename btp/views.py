from rest_framework.decorators import api_view
from rest_framework.response import Response
import math
import yfinance as yf
import datetime
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import uuid


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
    #truncate to 2 decimal places
    rate = math.trunc(rate * 100)
    return rate


def getFDrate(time):
    # Fixed deposit interest rates for popular banks in India (SBI Data)
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
    #truncate to 2 decimal places
    ci = math.trunc(ci * 100) / 100
    return ci


def createGraph(response):
    #takes response and creats bar graph and pie chart and saves it in static folder and returns the path
    """
     [
        "Instrument Name": "Saving Account",
        "Rate": rate,
        "Maturing Amount": ci],
        [
        "Instrument Name": "Fixed Deposit",
        "Rate": rate,
        "Maturing Amount": ci]
    ]
    """

    instruments = []
    return_amount = []
    for i in response:
        instruments.append(i['Instrument Name'])
        return_amount.append(i['Maturing Amount'])
    colors = [
        '#FFC300', '#FF5733', '#C70039', '#900C3F', '#581845', '#0074D9',
        '#2ECC40', '#FF851B', '#85144b'
    ]
    #bar 2D plot of return amount on different instruments
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.bar(instruments, return_amount, color=colors)
    ax.set_ylabel('Return Amount')
    ax.set_xlabel('Instruments')
    ax.set_xticklabels(instruments, rotation=45)
    ax.set_title('Return Amount on Different Instruments')

    name1 = "./static/bar3d"
    file_name1 = f"{name1}_{uuid.uuid4()}.png"
    file_path1 = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              file_name1)
    plt.savefig(file_path1)
    plt.close(fig)

    #pie chart of return amount on different instruments
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.pie(return_amount,
           labels=instruments,
           autopct='%1.1f%%',
           shadow=True,
           startangle=90)
    ax.axis('equal')
    name2 = "./static/pie"
    file_name2 = f"{name2}_{uuid.uuid4()}.png"
    file_path2 = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              file_name2)
    plt.savefig(file_path2)
    plt.close(fig)
    resp = {}
    resp['bar3d'] = file_name1.lstrip('./')
    resp['pie'] = file_name2.lstrip('./')
    return resp


@api_view(['GET'])
def finCal(request, amount, years, months):
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

    time = years + months / 12

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
    """
    json response with
    {
        "Amount Invested": amount,
        "Time": time,
        { [
            "Instrument Name": "Saving Account",
            "Rate": rate,
            "Maturing Amount": ci],
            [
            "Instrument Name": "Fixed Deposit",
            "Rate": rate,
            "Maturing Amount": ci],

        }
    }
    """
    response = {
        "Amount Invested": amount,
        "Time": time,
        "Financial Instruments": response_array
    }

    graph_url = createGraph(response_array)
    response['Graphs'] = graph_url
    return Response(response)


def createSIPGraph(invested_amount, est_return):
    #pie chart of invested amount and estimated return
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.pie([invested_amount, est_return],
           labels=['Invested Amount', 'Estimated Return'],
           autopct='%1.1f%%',
           shadow=True,
           startangle=90)
    ax.axis('equal')
    name2 = "./static/sipPie"
    file_name2 = f"{name2}_{uuid.uuid4()}.png"
    file_path2 = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              file_name2)
    plt.savefig(file_path2)
    plt.close(fig)
    return file_name2.lstrip('./')


@api_view(['GET'])
def sipCal(request, amount, time, rate):
    """
    This function takes in the monthly investment amount and the time period (in years) and calculate 
    maturing amount for SIP
    """
    no_of_investments = time * 12
    rate = float(rate)
    periodic_rate = rate / 12
    maturity_amount = amount * ((math.pow(
        (1 + periodic_rate / 100), no_of_investments) - 1) /
                                (periodic_rate / 100))
    #truncate to 2 decimal places
    maturity_amount = math.floor(maturity_amount * 100) / 100

    invested_amount = amount * no_of_investments
    est_return = maturity_amount - invested_amount
    #truncate to 2 decimal places
    est_return = math.floor(est_return * 100) / 100
    total_value = maturity_amount
    response = {
        "Invested Amount": invested_amount,
        "Estimated Return": est_return,
        "Total Value": total_value
    }
    print(maturity_amount, invested_amount, est_return, total_value)

    graph_url = createSIPGraph(invested_amount, est_return)
    response['Graphs'] = graph_url
    return Response(response)