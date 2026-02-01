
from openai import OpenAI
import getpass, os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say: Working!"}],
    max_tokens=5
)

print(f"✓ Success! Response: {response.choices[0].message.content}")
print(f"Cost: ${response.usage.total_tokens * 0.000000375:.6f}")