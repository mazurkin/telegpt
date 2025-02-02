import os
import openai

from .ai import AbstractSummarizer


class OpenAiSummarizer(AbstractSummarizer):

    ENV_KEY: str = 'OPENAI_API_KEY'

    MODEL: str = 'gpt-4o-mini'

    TEMPERATURE: float = 0.01

    def summarize(self, system: str, prompt: str) -> str:
        api_key: str = os.environ[self.ENV_KEY]

        client = openai.OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model=self.MODEL,
            temperature=self.TEMPERATURE,
            messages=[
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': prompt},
            ],
            stream=False,
        )

        return response.choices[0].message.content
