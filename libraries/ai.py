import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('.env')

class OpenAIClient:
    """
    A class to interact with OpenAI's GPT models.
    """
    def __init__(self):
        """
        Initializes the OpenAIClient and loads the API key from the environment variables.
        """
        self.client = OpenAI(api_key=os.getenv('OPEN_AI_KEY'))

    def get_chat_completion(self, messages, model="gpt-3.5-turbo"):
        """
        Interacts with the specified OpenAI GPT model using the provided messages.

        :param messages: A list of message dictionaries to send to the OpenAI API.
        :param model: The model to use for generating completions. Default is "gpt-3.5-turbo".
        :return: The response from the OpenAI API.
        """
        return self.client.chat.completions.create(messages=messages, model=model)
