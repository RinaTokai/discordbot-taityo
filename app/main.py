from core.start import DBot
import discord
import os

from servers.main_server import keep_alive

keep_alive()

Token=os.environ['TOKEN']

DBot(Token,discord.Intents.all()).run()