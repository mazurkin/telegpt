import abc


class AbstractSummarizer(abc.ABC):
    """
    Abstract summarizer
    """

    @abc.abstractmethod
    def summarize(self, system: str, prompt: str) -> str:
        pass
