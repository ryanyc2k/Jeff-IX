#!/usr/bin/env python3

# bot.py
import os
import random
import discord
from discord.ext import commands
from dotenv import load_dotenv
from forex_python.converter import CurrencyRates
from forex_python.bitcoin import BtcConverter
from pyowm import OWM

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
WEATHER = os.getenv('WEATHER_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.presences = True

cr = CurrencyRates()
bc = BtcConverter()

owm = OWM(WEATHER)
mgr = owm.weather_manager()

bot = commands.Bot(intents=intents, command_prefix='$')

@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)

    # Set "Watching" status
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="you"))

    print(
        f'{bot.user.name}: Successfully connected to {guild.name} (id: {guild.id})\n'
    )

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    greetings = [
        f'Hello {message.author.mention}',
        f'Hola {message.author.mention}',
        f'Bonjour {message.author.mention}',
        f'Hallo {message.author.mention}',
        f'Hej {message.author.mention}',
        f'Hei {message.author.mention}',
        f'Hallå {message.author.mention}',
        f'你好 {message.author.mention}',
        f'Здравствуйте {message.author.mention}',
        f'Ciao {message.author.mention}',
        f'Ahoj {message.author.mention}',
        f'Zdravo {message.author.mention}',
        f'γεια {message.author.mention}',
        f'{message.author.mention} مرحبا',
        f'{message.author.mention} שלום',
        f'Aloha {message.author.mention}',
        f'こんにちは {message.author.mention}',
        f'안녕하세요 {message.author.mention}',
        f'Witaj {message.author.mention}',
        f'Olá {message.author.mention}',
        f'Merhaba {message.author.mention}',
        f'Xin chào {message.author.mention}'
    ]

    if bot.user.mentioned_in(message) and message.mention_everyone is False:
        response = random.choice(greetings)
        await message.channel.send(response)

    await bot.process_commands(message)

# error reporting
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.NoPrivateMessage):
        return await ctx.send('Sorry, this command cannot be used in private messages.')
    if isinstance(error, commands.errors.CheckFailure):
        return await ctx.send('You do not have the required role to use this command.')
    if isinstance(error, commands.errors.MissingRequiredArgument):
        return await ctx.send(f'Invalid usage. Use \'$help {ctx.command}\' for more info.')

# currency converter using forex-python
@bot.command(name='cc',
    brief='Converts amount from orig to new currency. Use $help cc for more info.',
    description=('Usage: $cc <amount> <orig_currency> <new_currency>')
)
async def cc(ctx, amt:float, orig_c, new_c):
    upper_orig_c = orig_c.upper()
    upper_new_c = new_c.upper()
    value = cr.convert(upper_orig_c, upper_new_c, amt)
    response = f'{amt:.2f} {upper_orig_c} = {value:.2f} {upper_new_c}'
    await ctx.send(response)

# convert bitcoin to currency using forex-python
@bot.command(name='frombtc',
    brief='Converts amount in BTC to desired currency. Use $help frombtc for more info.',
    description=('Usage: $frombtc <amount> <currency>')
)
async def frombtc(ctx, amt:float, curr):
    upper_curr = curr.upper()
    value = bc.convert_btc_to_cur(amt, upper_curr)
    response = f'{amt} BTC = {value:.2f} {upper_curr}'
    await ctx.send(response)

# convert currency to bitcoin using forex-python
@bot.command(name='tobtc',
    brief='Converts amount in desired currency to BTC. Use $help tobtc for more info.',
    description=('Usage: $tobtc <amount> <currency>')
)
async def tobtc(ctx, amt:float, curr):
    upper_curr = curr.upper()
    value = bc.convert_to_btc(amt, upper_curr)
    response = f'{amt:.2f} {upper_curr} = {value} BTC'
    await ctx.send(response)

# obtain weather data with OpenWeatherMap and pyowm
@bot.command(name='weather',
    brief='Get weather data from OpenWeatherMap.',
    description=('Usage: $weather <location>\n'
        'You may include the country after the city name if you wish, separated by a comma. ex "$weather london,uk"')
)
async def weather(ctx, *args):
    location = ' '.join(args)
    observation = mgr.weather_at_place(location)
    w = observation.weather
    temp = w.temperature(unit='fahrenheit')
    humidity = w.humidity
    status = w.detailed_status
    sunrise = w.sunrise_time(timeformat='date')
    sunset = w.sunset_time(timeformat='date')

    response = (f'Weather data for {location.capitalize()}.\n'
            f'**Status**: {status}\n'
            f'**Temperature**: {temp["temp"]:.2f}F / {((temp["temp"] - 32) / 1.8):.2f}C\n'
            f'**High**: {temp["temp_max"]:.2f}F / {((temp["temp_max"] - 32) / 1.8):.2f}C\n'
            f'**Low**: {temp["temp_min"]:.2f}F / {((temp["temp_min"] - 32) / 1.8):.2f}C\n'
            f'**Feels like**: {temp["feels_like"]:.2f}F / {((temp["feels_like"] - 32) / 1.8):.2f}C\n'
            f'**Humidity**: {humidity}%\n'
            f'**Sunrise**: {sunrise} UTC\n'
            f'**Sunset**: {sunset} UTC')
    await ctx.send(response)

# bot say - Admin only
@bot.command(name='say',
    brief='Use the bot to say something. Admins only.')
@commands.has_role('Admin')
async def say(ctx, *args):
    guild = ctx.guild
    message = ' '.join(args)

    await ctx.message.delete()
    await ctx.send(message)

# bot announcement - Admin only
@bot.command(name='announce',
    brief='Use the bot to make an announcement. Admins only.')
@commands.has_role('Admin')
async def announce(ctx, *args):
    guild = ctx.guild
    message = ' '.join(args)
    announcement_channel = discord.utils.get(guild.channels, name='announcements')

    await ctx.message.delete()
    await announcement_channel.send(message)

bot.run(TOKEN)
