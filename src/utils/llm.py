import os
from typing import Type, TypeVar
import logging

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

T = TypeVar("T", bound=BaseModel)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(
    api_key=ANTHROPIC_API_KEY
)


async def extract_structured(schema: Type[T], messages: list[dict], system: str = "") -> T:
    kwargs = {}
    if system:
        kwargs["system"] = system

    response = client.messages.parse(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        messages=messages,
        output_format=schema,
        **kwargs,
    )
    logging.warning(f"response: {response.parsed_output}")
    return response.parsed_output
