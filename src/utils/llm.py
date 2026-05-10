import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

LLM_MODEL = os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct:novita")

def OpenAISetup() -> AsyncOpenAI:
    return AsyncOpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=os.environ["HF_TOKEN"],
    )
