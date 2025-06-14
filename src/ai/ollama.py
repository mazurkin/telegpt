import typing as t
import ollama

from .ai import AbstractAI


class OllamaAI(AbstractAI):

    MODEL: str = 'gemma3:12b'

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
