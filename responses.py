import random
import openai
from dotenv import dotenv_values

config = dotenv_values(".env")
openai.api_key = config["OPENAI_KEY"]

def handle_response(message):
    response = openai.Completion.create(
      model = "text-davinci-003",
      prompt = message,
      temperature = 0.9,
      max_tokens = 1024,
      top_p = 1,
      frequency_penalty = 0,
      presence_penalty = 0.6,
      stop=[" Human:", " AI:"]
    )

    return response.choices[0].text