from .ai import AbstractAI


class NullAI(AbstractAI):
    """
    AI just returns the same prompt in response
    """

    def summarize(self, system: str, prompt: str) -> str:
        return prompt
