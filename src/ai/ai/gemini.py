import os
import google.generativeai

from .ai import AbstractSummarizer


class GeminiSummarizer(AbstractSummarizer):

    ENV_KEY: str = 'GOOGLE_AI_KEY'

    MODEL: str = 'gemini-1.5-pro'

    TEMPERATURE: float = 0.01

    MAX_TOKENS: int = 16384

    def summarize(self, system: str, prompt: str) -> str:
        api_key: str = os.environ[self.ENV_KEY]

        google.generativeai.configure(api_key=api_key, transport='rest')

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
