from .ai import AbstractSummarizer


class ReflectSummarizer(AbstractSummarizer):

    def summarize(self, system: str, prompt: str) -> str:
        return prompt
