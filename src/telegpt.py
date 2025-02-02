"""
TeleGpt - AI summarizer for the telegram chats
"""

import enum
import os
import logging
import logging.config
import sys
import typing as t
import argh
import pathlib
import pytz
import tzlocal
import yaml
import datetime
import dataclasses

import ai
import telegram


@dataclasses.dataclass
class TeleGptSummarizerDescriptor:
    """
    Information about specific LLM engine
    """

    # specific client class
    ai: t.Type[ai.AbstractAI]


class TeleGptSummarizer(enum.Enum):
    """
    Type of LLM engine
    """

    # return the prompt itself
    NULL = TeleGptSummarizerDescriptor(ai=ai.NullAI)

    # Ollama local API
    OLLAMA = TeleGptSummarizerDescriptor(ai=ai.OllamaAI)

    # Gemini remote API
    GEMINI = TeleGptSummarizerDescriptor(ai=ai.GeminiAI)

    # DeepSeek remote API
    DEEPSEEK = TeleGptSummarizerDescriptor(ai=ai.DeepSeekAI)

    # OpenAI remote API
    OPENAI = TeleGptSummarizerDescriptor(ai=ai.OpenAI)

    @classmethod
    def parse(cls, value: str) -> 'TeleGptSummarizer':
        return cls[value]

    def descriptor(self) -> TeleGptSummarizerDescriptor:
        return self.value


class TeleGptApplication:

    TIMEZONE: pytz.tzinfo = pytz.timezone(tzlocal.get_localzone_name())

    SYSTEM_PROMPT_FILE: str = 'system.txt'

    DEFAULT_PROMPT_FILE: str = 'prompt.txt'

    def __init__(self):
        # moment when the application has started
        self.started: datetime.datetime = datetime.datetime.now(tz=self.TIMEZONE)

        # script path
        self.app_src_path: pathlib.Path = pathlib.Path(__file__)
        self.app_dir_path: pathlib.Path = self.app_src_path.parent.resolve()

        # package and source code folders
        self.src_dir_path: pathlib.Path = self.app_dir_path.resolve()
        self.pkg_dir_path: pathlib.Path = self.src_dir_path.parent.resolve()

        # session location
        self.session_path: pathlib.Path = self.pkg_dir_path.joinpath('session').joinpath('telegpt.session')

        # init logging
        self.init_logging()

    def init_logging(self):
        # load logging configuration
        logging_config_path = self.app_dir_path / 'logging.yaml'

        with open(logging_config_path, 'rt') as file:
            yaml_text = file.read()

        logging_config = yaml.load(yaml_text, yaml.SafeLoader)
        logging.config.dictConfig(logging_config)

        logging.info('Using logging configuration [%s]', logging_config_path)

    @argh.arg('--app-id', type=str, required=False, help='application identifier')
    @argh.arg('--app-hash', type=str, required=False, help='application hash')
    @argh.arg('--phone', type=str, required=False, help='the phone number of the Telegram account')
    @argh.arg('--prompt', type=str, required=False, help='the name of the prompt file')
    @argh.arg('--chat', type=str, required=False, help='chat name')
    @argh.arg('--date', type=str, required=False, help='chat date (for example "2025-01-01"')
    @argh.arg('--summarizer', type=TeleGptSummarizer.parse, required=False, help='type of LLM engine for summarizing')
    def main(self,
             app_id: t.Optional[int] = None,
             app_hash: t.Optional[str] = None,
             phone: t.Optional[str] = None,
             chat: t.Optional[str] = None,
             date: t.Optional[str] = None,
             summarizer: TeleGptSummarizer = TeleGptSummarizer.OLLAMA,
             prompt: str = DEFAULT_PROMPT_FILE,
             ):
        # log the arguments
        logging.info('Using arguments: %s', sys.argv)
        logging.info('Using timezone: %s', self.TIMEZONE)
        logging.info('Using prompt: %s', prompt)

        # lookup for the default values for the parameters
        if not app_id:
            app_id = int(os.environ['TELEGPT_APP_ID'])

        if not app_hash:
            app_hash = os.environ['TELEGPT_APP_HASH']

        if not phone:
            phone = os.environ['TELEGPT_PHONE']

        if not chat:
            chat = os.environ['TELEGPT_CHAT']

        if not summarizer:
            summarizer = TeleGptSummarizer.parse(os.environ['TELEGPT_SUMMARIZER'])

        if not date:
            date = datetime.datetime.now(tz=self.TIMEZONE).strftime('%Y-%m-%d')

        # fetch the conversation
        logging.info('Requesting chat history')
        conversation: t.List[str] = self.fetch_conversation(app_id, app_hash, phone, chat, date)

        # summarize the conversation
        logging.info('Requesting AI summary with "%s"', summarizer.name)
        response = self.summarize_conversation(summarizer, prompt, conversation)

        # log the conversation
        logging.info('TELEGPT(chat: "%s", day: "%s", ai: "%s"):\n\n%s', chat, date, summarizer.name, response)

    def fetch_conversation(self, app_id: int, app_hash: str, phone: str, chat: str, date: str) -> t.List[str]:
        client = telegram.Telegram(
            session=self.session_path,
            api_id=app_id,
            api_hash=app_hash,
            phone=phone,
            timezone=self.TIMEZONE,
        )

        return client.conversation(chat, date)

    def load_prompt(self, prompt_file: str) -> str:
        prompt_file_path: pathlib.Path = self.pkg_dir_path.joinpath('prompt').joinpath(prompt_file)

        with open(prompt_file_path, 'tr') as f:
            content = f.read()

        content = content.strip()

        return content

    def summarize_conversation(self, summarizer: TeleGptSummarizer, prompt_file: str, conversation: t.List[str]) -> str:
        if not conversation:
            return 'There is no any conversation today in the chat!'

        content = '\n'.join(conversation)

        system_text = self.load_prompt(self.SYSTEM_PROMPT_FILE)

        prompt_template = self.load_prompt(prompt_file)
        prompt_text = prompt_template.format(content=content)

        client = summarizer.descriptor().ai()
        return client.summarize(system_text, prompt_text)


if __name__ == '__main__':
    application = TeleGptApplication()
    argh.dispatch_command(application.main)
