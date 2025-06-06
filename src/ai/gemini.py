import os
import google.generativeai

from .ai import AbstractAI


class GeminiAI(AbstractAI):

    ENV_KEY: str = 'GEMINI_API_KEY'

    MODEL: str = 'gemini-2.0-flash'

    TEMPERATURE: float = 0.01

    MAX_TOKENS: int = 16384

    TRANSPORT: str = 'rest'

    def __init__(self):
        self.api_key: str = os.environ[self.ENV_KEY]
        google.generativeai.configure(api_key=self.api_key, transport=self.TRANSPORT)

    def summarize(self, system: str, prompt: str) -> str:
        model = google.generativeai.GenerativeModel(
            model_name=self.MODEL,
            system_instruction=system,
        )

        response = model.generate_content(
            prompt,
            safety_settings='BLOCK_NONE',
            generation_config=google.generativeai.GenerationConfig(
                max_output_tokens=self.MAX_TOKENS,
                temperature=self.TEMPERATURE,
            )
        )

        return response.text
