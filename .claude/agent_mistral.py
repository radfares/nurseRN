import os

from mistralai import Mistral

client = Mistral(api_key=os.environ.get("MISTRAL_API_KEY"))

response = client.beta.conversations.start(
    agent_id="ag_019ad730d7ce73319176f3244b28b8d1",
    inputs="Hello there!",
)

print(response)
