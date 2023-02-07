import discord
import responses
import asyncio
import math
from io import StringIO
from dotenv import dotenv_values

client = discord.Client(intents = discord.Intents.all())

async def send_response_in_file(message, response, is_private):
    buffer = StringIO(response)
    f = discord.File(buffer, filename = "response.txt")
    await message.channel.send(file = f)

async def send_response_in_slide(message, response, is_private):
    per_page = 800
    pages = math.ceil(len(response) / per_page)
    cur_page = 1
    chunk = response[:per_page]
    slide = await message.channel.send(f"```Page {cur_page}/{pages}:\n{chunk}```")
    await slide.add_reaction("◀️")
    await slide.add_reaction("▶️")
    active = True

    def check(reaction, user):
        return user == message.author and str(reaction.emoji) in ["◀️", "▶️"]

    while active:
        try:
            reaction, user = await client.wait_for("reaction_add", timeout = 60, check = check)
        
            if str(reaction.emoji) == "▶️" and cur_page != pages:
                cur_page += 1
                if cur_page != pages:
                    chunk = response[(cur_page - 1) * per_page:cur_page * per_page]
                else:
                    chunk = response[(cur_page - 1) * per_page:]
                await slide.edit(content = f"```Page {cur_page}/{pages}:\n\n{chunk}```")
                await slide.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "◀️" and cur_page > 1:
                cur_page -= 1
                chunk = response[(cur_page - 1) * per_page:cur_page * per_page]
                await slide.edit(content=f"```Page {cur_page}/{pages}:\n\n{chunk}```")
                await slide.remove_reaction(reaction, user)
        except asyncio.TimeoutError:
            active = False

async def handle_long_message(message, response, is_private):
    embed = discord.Embed(
                description = "The response is too long. \nDo you want it in the form of a file ( 1️⃣ ) or slides ( 2️⃣ )?",
                color = discord.Colour.yellow()
            )

    warning = await message.channel.send(embed = embed)
    await warning.add_reaction("1️⃣")
    await warning.add_reaction("2️⃣")

    def check(reaction, user):
        return user == message.author and str(reaction.emoji) in ["1️⃣", "2️⃣"]
    
    reaction, user = await client.wait_for('reaction_add', timeout = 60.0, check = check)
    if str(reaction.emoji) == "1️⃣":
        await send_response_in_file(message, response, is_private)
    elif str(reaction.emoji) == "2️⃣":
        await send_response_in_slide(message, response, is_private)

async def send_message(message, user_message, is_private):
    try:
        response = responses.handle_response(user_message)
        if len(response) < 2000:
            response = "```" + response + "```"
            await message.author.send(response) if is_private else await message.channel.send(response) 
        else:
            await handle_long_message(message, response, is_private)
    except Exception as e:
        print(e)

def run_bot():
    config = dotenv_values(".env")

    @client.event
    async def on_ready():
        print(f'{client.user} is running')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        user_message = str(message.content)

        if user_message.startswith("!chat "):
            user_message = user_message[6:]
            await send_message(message, user_message, is_private = False)
        elif user_message.startswith("!help"):
            embed = discord.Embed(
                title = "Here's how to use Ubibot: ",
                description = "`!chat ` Your message.",
                color = discord.Colour.green()
            )
            await message.channel.send(embed = embed)

    client.run(config["TOKEN"])