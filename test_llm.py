import os
import asyncio
from litellm import acompletion
from dotenv import load_dotenv

load_dotenv()

async def main():
    models = ['gemini/gemini-2.5-flash', 'gemini/gemini-3.5-flash-lite', 'gemini/gemini-3-flash-preview', 'gemini/gemini-2.5-pro']
    for model in models:
        try:
            res = await acompletion(model=model, messages=[{"role": "user", "content": "hi"}])
            print(f"SUCCESS: {model}")
            return
        except Exception as e:
            print(f"FAIL: {model} - {str(e)[:50]}")

asyncio.run(main())
