import discord
import boto3

# Set up the AWS Translate client
translate = boto3.client('translate', region_name='REGION')

# Set up the Discord client
client = discord.Client(intents=discord.Intents.all())

# Set the ID of the channel where translation is allowed
allowed_channel_id = CHANNEL_ID

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == client.user:
        return

    # Ignore empty messages
    if not message.content:
        return

    # Only translate messages sent in the allowed channel
    if message.channel.id != allowed_channel_id:
        return

    # Translate the message content to Traditional Chinese
    response = translate.translate_text(Text=message.content, SourceLanguageCode='SOURCE_LANGUAGE_CODE', TargetLanguageCode='TRANSALTE_LANGUAGE_CODE')

    # Send the translated message to the same channel
    await message.channel.send(response.get('TranslatedText'))

# Run the bot
client.run('DISCORD_BOT_TOKEN')
