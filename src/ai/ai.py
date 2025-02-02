import abc


class AbstractAI(abc.ABC):
    """
    Abstract summarizer
    """

    @abc.abstractmethod
    def summarize(self, system: str, prompt: str) -> str:
        pass
