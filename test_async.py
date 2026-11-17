import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def main():
    url = f"https://api.telegram.org/bot{TOKEN}/getMe"

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url)
        print("Status:", response.status_code)
        print(response.text[:500])

asyncio.run(main())