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
import telethon
import datetime

import ollama


class TeleGptApplication:

    TIMEZONE: pytz.tzinfo = pytz.timezone(tzlocal.get_localzone_name())

    MESSAGE_LIMIT: int = 2500

    LLM_MODEL: str = 'phi4:14b'

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
    @argh.arg('--app-phone', type=str, required=False, help='application phone')
    @argh.arg('--chat', type=str, required=False, help='chat name')
    @argh.arg('--date', type=str, required=False, help='chat date')
    def main(self,
             app_id: t.Optional[int] = None,
             app_hash: t.Optional[str] = None,
             app_phone: t.Optional[str] = None,
             chat: t.Optional[str] = None,
             date: t.Optional[str] = None,
             ):
        # log the arguments
        logging.info('Using arguments: %s', sys.argv)
        logging.info('Using timezone: %s', self.TIMEZONE)

        # lookup for the default values for the parameters
        if not app_id:
            app_id = int(os.environ['TELEGPT_APP_ID'])

        if not app_hash:
            app_hash = os.environ['TELEGPT_APP_HASH']

        if not app_phone:
            app_phone = os.environ['TELEGPT_PHONE']

        if not chat:
            chat = os.environ['TELEGPT_CHAT']

        if not date:
            date = datetime.datetime.now(tz=self.TIMEZONE).strftime('%Y-%m-%d')

        conversation: t.List[str] = self.fetch(app_id, app_hash, app_phone, chat, date)

        response = self.contextualize(conversation)
        logging.info('TELEGPT(chat: "%s", day: "%s"):\n\n%s', chat, date, response)

    def fetch(self, app_id: int, app_hash: str, app_phone: str, chat: str, date: str) -> t.List[str]:
        client = telethon.TelegramClient(
            session=str(self.session_path.resolve()),
            api_id=app_id,
            api_hash=app_hash,
        )

        conversation: t.List[str] = []

        async def process():
            await client.connect()

            if not await client.is_user_authorized():
                await client.send_code_request(app_phone)
                await client.sign_in(app_phone, input('Enter the code: '))

            profile = await client.get_me()
            logging.info('Logged in as [%s %s %s]', profile.first_name, profile.last_name, profile.phone)

            # fetch all dialogs
            chat_id: t.Optional[int] = None
            async for dialog in client.iter_dialogs():
                logging.debug('dialog "%s"=%s', dialog.name, dialog.id)

                if dialog.name == chat:
                    chat_id = dialog.id

            if not chat_id:
                raise ValueError('Chat is not found: ' + chat)

            # define the day
            date_offset = datetime.datetime.strptime(date, '%Y-%m-%d')
            date_offset = self.TIMEZONE.localize(date_offset)

            # fetch all messages
            messages = client.iter_messages(
                entity=chat_id,
                limit=self.MESSAGE_LIMIT,
                offset_date=date_offset,
                reverse=True,
            )

            async for message in messages:
                if not message.text:
                    continue
                if 'TELEGPT' in message.text:
                    continue

                message_text = message.text.replace('\n', ' ').replace('\r', '')

                message_date: datetime.datetime = message.date.astimezone(self.TIMEZONE)
                if message_date.date() != date_offset.date():
                    break

                message_author: str
                if message.sender.first_name and message.sender.last_name:
                    message_author = message.sender.first_name + ' ' + message.sender.last_name
                elif message.sender.first_name:
                    message_author = message.sender.first_name
                elif message.sender.last_name:
                    message_author = message.sender.last_name
                else:
                    message_author = str(message.sender.id)

                logging.debug(
                    '%s, %s: [%s] %s',
                    message.id,
                    message_date.strftime('%Y-%m-%d %H:%M:%S'),
                    message_author,
                    message_text,
                )

                conversation.append(f'"{message_author}": {message_text}')

        with client:
            client.loop.run_until_complete(process())

        return conversation

    def contextualize(self, conversation: t.List[str]) -> str:
        prompt = """
        You are the expert who analyses conversation between multiple friends.
        You will be questioned with questions. You have to answer every question in the most detailed way quoting
        the original text from the conversation.
        Answer all questions in English language.
        """

        content = '\n'.join(conversation)

        query = f"""
        Conversation is a plain text in form of multiple lines.
        Every line represents one single messages. In each line first goes the author name in quotes
        and then after semicolon goes the message of this author.
        The messages are usually short and sometimes they could be a response to some of the previous messages.
        Sometimes slang and some specific terminology is used.
        You must make honest and precise analysis of this conversation, show some direct quotes from the conversation.
        The conversation starts from the next line and the questions come after the conversation.

        {content}

        Question: What are the topics discussed in this conversation, explain in details?
        Question: Who is the most active author in this conversation?
        Question: Who from the authors has made more comments than the others?
        Question: Is there any kind of profanity or aggressive, sarcastic, rude language used in this conversation?
        Question: Is there any hot topic the most of people had discussed in this conversation?
        Question: List all the full web links mentioned in this conversation?
        Question: Is there any discussion of politics in USA in this conversation?
        Question: Is there any discussion of politics in Russia in this conversation?
        Question: Is there any discussion of politics in general in this conversation?
        Question: Did anyone mention USA as a country or any city in USA in negative context in this conversation?
        Question: Has been Hitler mentioned and who has mentioned him in this conversation?
        """

        options: t.Dict = {
            'temperature': 0.1,
        }

        response: ollama.ChatResponse = ollama.generate(
            model=self.LLM_MODEL,
            prompt=query,
            options=options,
            system=prompt,
        )

        return response.response


if __name__ == '__main__':
    application = TeleGptApplication()
    argh.dispatch_command(application.main)
