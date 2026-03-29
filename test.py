import asyncio
from dotenv import load_dotenv
load_dotenv()  # load .env before anything else

from backend.gemini import call_gemini

async def test():
    response = await call_gemini("Say hello and confirm you are working. Keep it under 20 words.")
    print(response)

asyncio.run(test())