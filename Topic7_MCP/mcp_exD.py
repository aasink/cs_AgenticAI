import requests
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
asta_key = os.getenv("ASTA_API_KEY")


openai_client = OpenAI(api_key=openai_key)

ASTA_URL = "https://asta-tools.allen.ai/mcp/v1"
asta_headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "x-api-key": asta_key
}