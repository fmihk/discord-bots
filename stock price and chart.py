import discord
import yfinance as yf
import requests
import os

from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from datetime import datetime, timedelta

intents = discord.Intents.all()
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('$'):
        ticker = message.content.split()[0][1:]

        try:
            # Get current stock data from Yahoo Finance
            stock_data = yf.Ticker(ticker).info
            stock_exchange = stock_data['exchange']
            stock_price = round(stock_data['regularMarketPrice'], 2)
            stock_change = stock_data['regularMarketChange']
            stock_percent_change = stock_data['regularMarketChangePercent']
            company_name = stock_data.get('longName', f'{ticker} (Futures)')

            # Get image from Finviz only if ticker is in US stock market
            if stock_exchange in ['NMS', 'NYQ', 'NAS']:
                url = f'https://finviz.com/chart.ashx?t={ticker}&ty=c&ta=1&p=d&s=l'
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(url, headers=headers)
            else:
                response = None

            # Create a Discord Embed
            color = discord.Color.green() if stock_change > 0 else discord.Color.red()
            embed = discord.Embed(
                title=f'{company_name} ({ticker.upper()})',
                description=f'Price: {stock_price}\nChange: {stock_change} ({stock_percent_change}%)',
                color=color
            )

            # Add image to the Embed if response is not None
            if response is not None:
                with open(f'{ticker}.png', 'wb') as f:
                    f.write(response.content)
                file = discord.File(f'{ticker}.png')
                embed.set_image(url=f'attachment://{ticker}.png')

            await message.channel.send(embed=embed, file=file if response is not None else None)

            # Delete the PNG file after sending the message
            if response is not None:
                os.remove(f'{ticker}.png')

        except KeyError:
            error_message = f'Error: {ticker} is not recognized as a stock. Please try a different ticker.'
            await message.channel.send(error_message)

        except Exception as e:
            error_message = f'Error: {str(e)}'
            await message.channel.send(error_message)

client.run('DISCORD_BOT_TOKEN')
