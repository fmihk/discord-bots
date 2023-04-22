import discord
import yfinance as yf
import pandas as pd
import os
import numpy as np
import urllib.request
from bs4 import BeautifulSoup
import requests
import json
import time

intents = discord.Intents.all()
intents.members = True

client = discord.Client(intents=intents)

api_key = os.environ.get('ALPHAVANTAGE_API_KEY')

def get_std_dev(ticker_symbol, period, filename):
    stock_data = yf.Ticker(ticker_symbol).history(period=period)
    company_info = yf.Ticker(ticker_symbol).info
    company_name = company_info['longName'] if 'longName' in company_info else ticker_symbol
    stock_data.to_csv(filename)
    time.sleep(1)  # add a short delay to allow file to fully write to disk
    std_dev = stock_data['Close'].std()
    price_std_dev = std_dev
    percentage_std_dev = std_dev / stock_data['Close'].mean() * 100
    return price_std_dev, percentage_std_dev, company_name

def get_current_price(ticker_symbol, period):
    stock_data = yf.download(ticker_symbol, period=period)
    if len(stock_data) == 0:
        return -1  # if no data is available, return -1
    return stock_data['Adj Close'].iloc[-1]  # return the last available closing price

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!sd'):
        ticker_symbol = message.content.split(' ')[1].upper()
        valid_periods = ['1wk', '2wk', '1mo', '3mo', '6mo', '1y']

        # Download data to CSV
        stock_data = yf.Ticker(ticker_symbol).history(period='max')
        csv_filename = f'{ticker_symbol}.csv'
        stock_data.to_csv(csv_filename)

        std_devs = {}
        for period in valid_periods:
            if period == '1y':
                current_price = get_current_price(ticker_symbol, period='1y')
            else:
                current_price = get_current_price(ticker_symbol, period=period) # specify the 'period' argument here
            current_price_float = float(current_price) if isinstance(current_price, (float, int)) else -1
            price_std_dev, percentage_std_dev, company_name = get_std_dev(ticker_symbol, period, csv_filename)
            price_std_dev_float = float(price_std_dev)
            if current_price_float >= 0:
                upper_price = f"{current_price_float + price_std_dev_float:.2f}"
                lower_price = f"{current_price_float - price_std_dev_float:.2f}"
            else:
                upper_price = "N/A"
                lower_price = "N/A"
            upper_percentage = percentage_std_dev
            lower_percentage = -percentage_std_dev
            std_devs[period] = {'price_sd': f"{price_std_dev:.2f}", 'upper_price': upper_price, 'lower_price': lower_price, 'percentage_sd': f"{percentage_std_dev:.2f}"}

        response = response = (f"The volatility of {company_name} for the following periods is:\n"
                    f"1 week: {std_devs['1wk']['price_sd']} ({std_devs['1wk']['percentage_sd']}%) and upper price: {std_devs['1wk']['upper_price']}, lower price: {std_devs['1wk']['lower_price']}\n"
                    f"2 weeks: {std_devs['2wk']['price_sd']} ({std_devs['2wk']['percentage_sd']}%) and upper price: {std_devs['2wk']['upper_price']}, lower price: {std_devs['2wk']['lower_price']}\n"
                    f"1 month: {std_devs['1mo']['price_sd']} ({std_devs['1mo']['percentage_sd']}%) and upper price: {std_devs['1mo']['upper_price']}, lower price: {std_devs['1mo']['lower_price']}\n"
                    f"3 months: {std_devs['3mo']['price_sd']} ({std_devs['3mo']['percentage_sd']}%) and upper price: {std_devs['3mo']['upper_price']}, lower price: {std_devs['3mo']['lower_price']}\n"
                    f"6 months: {std_devs['6mo']['price_sd']} ({std_devs['6mo']['percentage_sd']}%) and upper price: {std_devs['6mo']['upper_price']}, lower price: {std_devs['6mo']['lower_price']}\n"
                    f"1 year: {std_devs['1y']['price_sd']} ({std_devs['1y']['percentage_sd']}%) and upper price: {std_devs['1y']['upper_price']}, lower price: {std_devs['1y']['lower_price']}\n"
                    "Disclaimer: This information is provided for educational and informational purposes only. Do not use this information as the sole basis for making investment decisions. We are not liable for any losses or damages that may arise from your use of this information.")
        await message.channel.send(response)

        # Remove CSV file
        os.remove(csv_filename)

client.run('DISCORD_BOT_TOKEN')
