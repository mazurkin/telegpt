import typing as t
import ollama

from .ai import AbstractSummarizer


class OllamaSummarizer(AbstractSummarizer):

    MODEL: str = 'phi4:14b'

    TEMPERATURE: float = 0.01

    def summarize(self, system: str, prompt: str) -> str:

        options: t.Dict = {
            'temperature': self.TEMPERATURE,
        }

        response: ollama.ChatResponse = ollama.generate(
            model=self.MODEL,
            prompt=prompt,
            options=options,
            system=system,
        )

        return response.response
