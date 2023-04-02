import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import requests
from sumy.parsers.html import HtmlParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

intents = discord.Intents.all()
client = commands.client(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

def sumy_lsa_summarization(url, lang="english", count=5):
    parser = HtmlParser.from_url(url, Tokenizer(lang))
    stemmer = Stemmer(lang)
    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(lang)
    summary = summarizer(parser.document, count)
    return "\n\n".join([str(sentence) for sentence in summary])

@client.command(name='tldr')
async def tldr(ctx, url):
    print(f'tldr command called with URL: {url}')
    if url.startswith("http"):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                summarization = sumy_lsa_summarization(url)
                if summarization:
                    await ctx.send(summarization)
                else:
                    await ctx.send("Could not summarize the webpage.")
            else:
                await ctx.send("Error accessing the webpage. Please try again later.")
        except requests.Timeout:
            await ctx.send("Timeout error occurred while accessing the webpage.")
        except Exception as e:
            await ctx.send(f"An error occurred while summarizing the webpage: {str(e)}")
    else:
        await ctx.send("Invalid URL. Please input a valid URL.")

client.run('DISCORD_BOT_TOKEN')