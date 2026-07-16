import json
import os

import boto3
from dotenv import load_dotenv

load_dotenv()

MODEL_ID = "amazon.nova-lite-v1:0"

client = boto3.client(
    "bedrock-runtime",
    region_name=os.environ["AWS_DEFAULT_REGION"],
)


def _clean_response(text: str) -> str:
    """
    Removes markdown code fences if the model wraps
    JSON inside ```json ... ```.
    """

    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        # Remove opening fence
        lines = lines[1:]

        # Remove closing fence
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines)

    return text.strip()


def generate(
    prompt: str,
    *,
    temperature: float = 0.3,
    max_tokens: int = 4096,
) -> str:
    """
    Generates plain text from Nova Lite.
    """

    response = client.converse(
        modelId=MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": prompt,
                    }
                ],
            }
        ],
        inferenceConfig={
            "temperature": temperature,
            "maxTokens": max_tokens,
        },
    )

    text = response["output"]["message"]["content"][0]["text"]

    return _clean_response(text)


def generate_json(
    prompt: str,
    *,
    temperature: float = 0.2,
    max_tokens: int = 4096,
) -> dict:
    """
    Generates JSON from Nova Lite.
    """

    text = generate(
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return json.loads(text)