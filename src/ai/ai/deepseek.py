import os
import typing as t
import json
import requests

from .ai import AbstractSummarizer


class DeepSeekSummarizer(AbstractSummarizer):

    ENV_KEY: str = 'DEEPSEEK_API_KEY'

    URL: str = 'https://api.deepseek.com/chat/completions'

    MODEL: str = 'deepseek-reasoner'

    TEMPERATURE: float = 0.01

    MAX_TOKENS: int = 16384

    def summarize(self, system: str, prompt: str) -> str:
        api_key: str = os.environ[self.ENV_KEY]

        headers: t.Mapping[str, str] = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + api_key,
        }

        request_json: t.Mapping = {
            'model': self.MODEL,
            'messages': [
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': prompt},
            ],
            'stream': False,
        }

        request_text = json.dumps(request_json)

        response = requests.post(
            self.URL,
            timeout=300,
            headers=headers,
            data=request_text,
        )

        response.raise_for_status()

        response_text = response.content

        if response_text:
            response_json = json.loads(response_text)
            return response_json['choices'][0]['message']['content']

        return 'no response'
