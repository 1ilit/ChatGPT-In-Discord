import discord
import responses
from io import StringIO
from dotenv import dotenv_values

client = discord.Client(intents = discord.Intents.all())

async def send_response_in_file(message, response, is_private):
    buffer = StringIO(response)
    f = discord.File(buffer, filename = "response.txt")
    await message.channel.send(file = f)

async def handle_long_message(message, response, is_private):
    valid_reactions=["1️⃣", "2️⃣"]
    embed = discord.Embed(
                description = "The response is too long. \nDo you want it in the form of a file ( 1️⃣ ) or slides ( 2️⃣ )?",
                color = discord.Colour.yellow()
            )

    warning = await message.channel.send(embed = embed)
    await warning.add_reaction("1️⃣")
    await warning.add_reaction("2️⃣")

    def check(reaction, user):
        return user == message.author and str(reaction.emoji) in valid_reactions
    
    reaction, user = await client.wait_for('reaction_add', timeout = 60.0, check = check)
    if str(reaction.emoji) == "1️⃣":
        await send_response_in_file(message, response, is_private)
    elif str(reaction.emoji) == "2️⃣":
        await message.channel.send("dis is slide")

async def send_message(message, user_message, is_private):
    try:
        response = "```" + responses.handle_response(user_message) + "```"
        if len(response) < 2000:
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