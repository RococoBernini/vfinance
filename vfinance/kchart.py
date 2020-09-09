import yfinance as yf
import datetime as dt
import pandas as pd
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import numpy as np
from mplfinance.original_flavor import candlestick_ohlc
import os
import pyimgur


def main():
    stock = input("Press your stock symbol")
    x = chart_plot_upload(stock)
    print(x)




def chart_plot_upload(stock):
    yf.pdr_override()

    smaUsed = [5, 10, 20]


    timed = dt.timedelta(120)
    now = dt.datetime.now()
    start = now - timed - dt.timedelta(max(smaUsed)) # Within one year
    print(start)
    # start = dt.datetime(2010,1,1)
    # stock = input("Enter the stock symbol: ") #Asks for stock ticker
    # stock = 'BRK-B'

    prices = pdr.get_data_yahoo(stock, start, now) #Fetches stock price data, saves as data frame

    # Set Plot Grid
    fig, (axc, axkd) = plt.subplots(2,1, gridspec_kw={'height_ratios': [3, 1]}, sharex=True, figsize=(15,10))
    axv = axc.twinx()

    # Caculated All SMA
    for x in smaUsed:
        prices['SMA_' + str(x)] = prices['Adj Close'].rolling(window = x).mean()

    # Caculate Boolinger Bands
    BBperiod = 15
    stdev = 2
    prices['Boolinger Band SMA' + str(BBperiod)] = prices.iloc[:, 4].rolling(window = BBperiod).mean()
    prices['STDEV'] = prices.iloc[:, 4].rolling(window = BBperiod).std()
    prices['LowerBand'] = prices['Boolinger Band SMA' + str(BBperiod)] - stdev * prices['STDEV']
    prices['UpperBand'] = prices['Boolinger Band SMA' + str(BBperiod)] + stdev * prices['STDEV']
    prices['Date'] = mdates.date2num(prices.index) #creates a date column stored in number format (for OHCL bars)


    # Caculated 10.4.4 KD Value
    Period = 10
    K = 4
    D = 4
    prices['RolHigh'] = prices['High'].rolling(window = Period).max()
    prices['RolLow'] = prices['Low'].rolling(window = Period).min()
    prices["stok"] = ((prices["Adj Close"] - prices["RolLow"]) /(prices["RolHigh"] - prices["RolLow"])) * 100
    prices["K"] = prices["stok"].rolling(window=K).mean()  #Finds 10.4 stoch
    prices["D"] = prices["K"].rolling(window=D).mean()  #Finds 10.4.4 stoch
    prices["GD"] = prices["High"]  #Create GD column to store green dots



    prices = prices[max(smaUsed):]
    ohlc = []
    for i in prices.index:
        append_me = prices['Date'][i], prices['Open'][i], prices['High'][i], prices["Low"][i], prices["Adj Close"][i], prices["Volume"][i]
        ohlc.append(append_me)
    print(ohlc)
    print(prices)

    # Plot
    # Moving average
    for x in smaUsed:
        axc.plot(prices['SMA_' + str(x)], label = 'SMA_' + str(x) )

    # Volume
    axv.plot(prices['Volume'], color = 'Navy')
    # axv.axes.yaxis.set_ticklabels(range(0, 10000000))
    axv.set_ylim(0, 5* max(prices['Volume']))
    axv.set_ylabel("Volume (K)")
    axv.fill_between(prices['Date'],prices['Volume'], facecolor='Navy', alpha = 0.25)
    # axv.yaxis.set_major_formatter(mticker.FormatStrFormatter('%0.0e'))
    axv.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: format(int(x/1000), ',')))

    candlestick_ohlc(axc, ohlc, width=.5, colorup='g', colordown='r', alpha=0.75,)


    axc.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  #change x axis back to datestamps
    axc.xaxis.set_major_locator(mticker.MaxNLocator(8))  #add more x axis labels
    axc.legend()


    axkd.plot(prices['K'], label = 'K')
    axkd.plot(prices['D'], label = 'D')
    axkd.axhline(y = 80, xmin = 0, xmax = 1, color='gray',linestyle = '--')
    axkd.axhline(y = 20, xmin = 0, xmax = 1, color='gray',linestyle = '--')
    axkd.legend(loc='center left', bbox_to_anchor=(1, 0.85))

    axkd.tick_params(axis='x', rotation=45)  #rotate dates for readability

    axc.set_title(stock)


    # build folder
    
    # basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    # newdir = os.path.join(basedir, 'chart')
    # if os.path.exists(newdir) == False:
    #     os.mkdir(newdir)
    print("Starting Saving....")
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    print('Base_dir:'+ BASE_DIR)
    fig.savefig(os.path.join(BASE_DIR,'chart/fig1.png'))
    

    CLIENT_ID = "f99b6417ee666d3"
    PATH = os.path.join(BASE_DIR,'chart/fig1.png')
    im = pyimgur.Imgur(CLIENT_ID)
    uploaded_image = im.upload_image(PATH, title="Uploaded with PyImgur")

    # print(uploaded_image.link)
    return (uploaded_image.link)
    

if __name__ == "__main__":
    main()












