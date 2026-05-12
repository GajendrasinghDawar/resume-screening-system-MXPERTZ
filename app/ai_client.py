import os

from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

AZURE_ENDPOINT = os.getenv(
    "AZURE_ENDPOINT",
    "https://lasttry-openai-azure.cognitiveservices.azure.com",
)

client = AzureOpenAI(
    api_key=os.getenv("AZURE_API_KEY"),
    azure_endpoint=AZURE_ENDPOINT,
    api_version="2025-04-01-preview",
)
