import os

from dotenv import load_dotenv

load_dotenv()


class LLMClient:

    def __init__(self):

        self.provider = os.getenv(
            "LLM_PROVIDER",
            "groq",
        )

        self.model = os.getenv(
            "LLM_MODEL",
            "llama-3.1-8b-instant",
        )

        self.api_key = os.getenv(
            "LLM_API_KEY"
        )

        if not self.api_key:
            raise ValueError(
                "LLM_API_KEY is not configured."
            )

    def generate(self, prompt: str) -> str:

        if self.provider == "groq":
            return self._generate_groq(prompt)

        raise ValueError(
            f"Unsupported LLM provider: {self.provider}"
        )

    def _generate_groq(self, prompt: str) -> str:

        from groq import Groq

        client = Groq(
            api_key=self.api_key
        )

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.1,
        )

        return response.choices[0].message.content
