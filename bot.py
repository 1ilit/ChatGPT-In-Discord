import discord
import responses
from dotenv import dotenv_values

async def send_message(message, user_message, is_private):
    try:
        response = responses.handle_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

def run_bot():
    config = dotenv_values(".env")

    client = discord.Client(intents = discord.Intents.all())

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