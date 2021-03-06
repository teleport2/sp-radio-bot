# -*- coding: utf-8 -*-

"""
SP radio discord bot
~~~~~~~~~~~~~~~~~~~

A discord bot that broadcasts Internet radio SP radio

:copyright: (c) 2022 Stepan Khozhempo
:license: MIT

"""

import discord
from bs4 import BeautifulSoup
import requests
from discord.ext import commands, tasks
import platform
import os
import asyncio
from dislash import InteractionClient

import TOKEN
import config as cfg

client = commands.Bot(command_prefix=cfg.command_prefix, help_command=None)
last_song = ''
inter_client = InteractionClient(client)


async def change_activity():
    global last_song

    try:
        html_getter = requests.get(cfg.radio_parameters_url)
        html_getter.encoding = 'utf-8'
        page = BeautifulSoup(html_getter.text, 'xml')
        song = page.find_all('tr')[10].find('td', {'class': 'streamdata'}).text

        if song != last_song:
            last_song = song
            await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=song))

    except requests.exceptions.ConnectionError:
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='СП Радио'))


@client.event
async def on_ready():
    print('<-------Bot started------->')
    print(f"Logged in as {client.user.name}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")

    change_activity.start()


@tasks.loop(seconds=cfg.radio_request_song_time)
async def change_activity():
    global last_song

    try:
        html_getter = requests.get(cfg.radio_parameters_url)
        html_getter.encoding = 'utf-8'
        page = BeautifulSoup(html_getter.text, 'xml')
        song = page.find_all('tr')[10].find('td', {'class': 'streamdata'}).text

        if song != last_song:
            last_song = song
            await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=song))

    except requests.exceptions.ConnectionError:
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='СП Радио'))


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.message.delete()
        notify = await ctx.send('Данной команды не существует.')

        await asyncio.sleep(cfg.notify_time_auto_delete)
        await notify.delete()


@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is not None and after.channel is None:
        if before.channel.guild.voice_client and len(before.channel.members) == 1:
            before.channel.guild.voice_client.stop()
            await before.channel.guild.voice_client.disconnect()


@client.command(pass_context=True, aliases=['join', 'p', 'j'])
async def play(ctx):
    await ctx.message.delete()

    try:
        channel = client.get_channel(ctx.message.author.voice.channel.id)
        channel = await channel.connect()

    except AttributeError:
        pass

    except asyncio.exceptions.TimeoutError:
        pass

    except discord.errors.ClientException:
        notify = await ctx.send('Бот уже находится в канале')
        await asyncio.sleep(cfg.notify_time_auto_delete)
        await notify.delete()
        return

    if ctx.voice_client:
        source = discord.FFmpegPCMAudio(cfg.radio_url)
        channel.play(source)

    else:
        notify = await ctx.send('Вы не находитесь в каком либо канале')
        await asyncio.sleep(cfg.notify_time_auto_delete)
        await notify.delete()


@client.command(pass_context=True, aliases=['leave', 'l', 's'])
async def stop(ctx):
    await ctx.message.delete()

    if ctx.voice_client is None:
        notify = await ctx.send('Бот ни находится в каком либо канале')
        await asyncio.sleep(cfg.notify_time_auto_delete)
        await notify.delete()
        return

    elif ctx.author.voice.channel == ctx.voice_client.channel:
        ctx.guild.voice_client.stop()
        await ctx.guild.voice_client.disconnect()

    elif ctx.author.voice.channel != ctx.voice_client.channel:
        notify = await ctx.send('Вы не находитесь в канале в котором играет бот')
        await asyncio.sleep(cfg.notify_time_auto_delete)
        await notify.delete()


@client.command(pass_context=True, aliases=['help', 'h'])
async def help_command(ctx):
    await ctx.message.delete()

    embed = discord.Embed(title="Команды")
    embed.add_field(name="Оставновить воспроизведение", value="/sprstop\n!;leave\n!;stop\n!;s\n!;l", inline=False)
    embed.add_field(name="Включить воспроизведение", value="/sprplay\n!;join\n!;play\n!;p\n!;j", inline=True)
    notify = await ctx.send(embed=embed)
    await asyncio.sleep(cfg.notify_help_time_auto_delete)
    await notify.delete()


@inter_client.slash_command(description="Включает сп радио")
async def sprplay(ctx):
    try:
        channel = client.get_channel(ctx.author.voice.channel.id)
        channel = await channel.connect()

    except AttributeError:
        pass

    except asyncio.exceptions.TimeoutError:
        pass

    except discord.errors.ClientException:
        notify = await ctx.send('Бот уже находится в канале')
        await asyncio.sleep(cfg.notify_time_auto_delete)
        await notify.delete()
        return

    if ctx.guild.voice_client:
        source = discord.FFmpegPCMAudio(cfg.radio_url)
        channel.play(source)
        notify = await ctx.send('Включаемся')
        await asyncio.sleep(cfg.notify_time_auto_delete)
        await notify.delete()

    else:
        notify = await ctx.send('Вы не находитесь в каком либо канале')
        await asyncio.sleep(cfg.notify_time_auto_delete)
        await notify.delete()


@inter_client.slash_command(description="Выключает сп радио")
async def sprstop(ctx):
    try:
        if ctx.guild.voice_client is None:
            notify = await ctx.send('Бот ни находится в каком либо канале')
            await asyncio.sleep(cfg.notify_time_auto_delete)
            await notify.delete()
            return

        elif ctx.author.voice.channel == ctx.guild.voice_client.channel:
            ctx.guild.voice_client.stop()
            await ctx.guild.voice_client.disconnect()
            notify = await ctx.send('Отключаемся...')
            await asyncio.sleep(cfg.notify_time_auto_delete)
            await notify.delete()

        elif ctx.author.voice.channel != ctx.guild.voice_client.channel:
            notify = await ctx.send('Вы не находитесь в канале в котором играет бот')
            await asyncio.sleep(cfg.notify_time_auto_delete)
            await notify.delete()

    except AttributeError:
        notify = await ctx.send('Вы не находитесь в канале в котором играет бот')
        await asyncio.sleep(cfg.notify_time_auto_delete)
        await notify.delete()


client.run(TOKEN.TOKEN)
