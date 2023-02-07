import asyncio
import discord
import openai
import math
from io import StringIO
from dotenv import dotenv_values

client = discord.Client(intents = discord.Intents.all())
config = dotenv_values(".env")
openai.api_key = config["OPENAI_KEY"]

"""Checks for client events and runs the bot"""
def run_bot():
    @client.event
    async def on_ready():
        print(f"{client.user} is running")

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        user_message = str(message.content)

        if user_message.startswith("!chat "):
            user_message = user_message[6:]
            await send_message(message, user_message)
        elif user_message.startswith("!help"):
            embed = discord.Embed(
                title = "Here's how to use Ubibot: ",
                description = "`!chat ` Your message.",
                color = discord.Colour.green()
            )
            await message.channel.send(embed = embed)

    client.run(config["TOKEN"])

"""Processes and sends `user_message`"""
async def send_message(message, user_message):
    try:
        response = handle_response(user_message)
        if len(response) < 2000:
            response = "```" + response + "```"
            await message.channel.send(response) 
        else:
            await handle_long_message(message, response)
    except Exception as e:
        print(e)

"""Fetches and returns the response from openai"""
def handle_response(message):
    response = openai.Completion.create(
      model = "text-davinci-003",
      prompt = message,
      temperature = 0,
      max_tokens = 1024,
      top_p = 1,
      frequency_penalty = 0,
      presence_penalty = 0,
      stop = ["#\n"]
    )

    return response['choices'][0]['text']

"""Sends an embed notifying that the response is too long for a normal message with reactions - 
   (1) for sending in a file, (2) for sending in a slide. There is a 60 sec timeout."""
async def handle_long_message(message, response):
    embed = discord.Embed(
                description = "The response is too long. \nDo you want it in the form of a file ( 1️⃣ ) or slides ( 2️⃣ )?",
                color = discord.Colour.yellow()
            )

    warning = await message.channel.send(embed = embed)
    await warning.add_reaction("1️⃣")
    await warning.add_reaction("2️⃣")

    def check(reaction, user):
        return user == message.author and str(reaction.emoji) in ["1️⃣", "2️⃣"]
    
    reaction, user = await client.wait_for("reaction_add", timeout = 60.0, check = check)
    if str(reaction.emoji) == "1️⃣":
        await send_response_in_file(message, response)
    elif str(reaction.emoji) == "2️⃣":
        await send_response_in_slide(message, response)

"""Sends `response` as a txt file in the current channel"""
async def send_response_in_file(message, response):
    buffer = StringIO(response)
    f = discord.File(buffer, filename = "response.txt")
    await message.channel.send(file = f)

"""Sends `response` as slides in the current channel (there is a timeout tho)"""
async def send_response_in_slide(message, response):
    per_page = 800
    pages = math.ceil(len(response) / per_page)
    current_page = 1
    chunk = response[:per_page]
    slide = await message.channel.send(f"```Page {current_page}/{pages}:\n{chunk}```")
    await slide.add_reaction("◀️")
    await slide.add_reaction("▶️")
    active = True

    def check(reaction, user):
        return user == message.author and str(reaction.emoji) in ["◀️", "▶️"]

    while active:
        try:
            reaction, user = await client.wait_for("reaction_add", timeout = 60.0, check = check)
        
            if str(reaction.emoji) == "▶️" and current_page != pages:
                current_page += 1
                if current_page != pages:
                    chunk = response[(current_page - 1) * per_page:current_page * per_page]
                else:
                    chunk = response[(current_page - 1) * per_page:]
                await slide.edit(content = f"```Page {current_page}/{pages}:\n\n{chunk}```")
                await slide.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "◀️" and current_page > 1:
                current_page -= 1
                chunk = response[(current_page - 1) * per_page:current_page * per_page]
                await slide.edit(content = f"```Page {current_page}/{pages}:\n\n{chunk}```")
                await slide.remove_reaction(reaction, user)
        except asyncio.TimeoutError:
            active = False
