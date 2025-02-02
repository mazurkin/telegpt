import pathlib
import telethon
import datetime
import typing as t
import logging
import pytz


class Telegram:

    MESSAGE_LIMIT: int = 1000

    def __init__(self, session: pathlib.Path, api_id: int, api_hash: str, phone: str, timezone: pytz.tzinfo):
        self.session = session
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.timezone = timezone

    def conversation(self, chat: str, date: str) -> t.List[str]:
        client = telethon.TelegramClient(
            session=str(self.session.resolve()),
            api_id=self.api_id,
            api_hash=self.api_hash,
        )

        with client:
            coroutine: t.Coroutine = self.fetch_conversation_async(client, self.phone, chat, date)
            return client.loop.run_until_complete(coroutine)

    async def fetch_conversation_async(self,
                                       client: telethon.TelegramClient,
                                       phone: str,
                                       chat: str,
                                       date: str,
                                       ) -> t.List[str]:
        await client.connect()

        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            await client.sign_in(phone, input('Enter the code: '))

        profile = await client.get_me()
        logging.info('Logged in as [%s %s %s]', profile.first_name, profile.last_name, profile.phone)

        # fetch all dialogs
        chat_id: t.Optional[int] = None

        async for dialog in client.iter_dialogs():
            logging.debug('dialog %s: %s', dialog.id, dialog.name)

            if dialog.name == chat:
                chat_id = dialog.id

        if not chat_id:
            raise ValueError('Chat is not found: ' + chat)

        # define the day
        date_offset = datetime.datetime.strptime(date, '%Y-%m-%d')
        date_offset = self.timezone.localize(date_offset)

        # fetch all messages
        conversation: t.List[str] = []

        messages: t.AsyncIterator = client.iter_messages(
            entity=chat_id,
            limit=self.MESSAGE_LIMIT,
            offset_date=date_offset,
            reverse=True,
        )

        async for message in messages:
            # ignore a message without text
            if not message.text:
                continue

            # ignore a message from this tool
            if 'TELEGPT' in message.text:
                continue

            # stop if this message is published the next day
            message_date: datetime.datetime = message.date.astimezone(self.timezone)
            if message_date.date() != date_offset.date():
                break

            # the information
            message_author: str = self.get_message_author(message)
            message_text: str = self.get_message_text(message)

            # the original message if this message is a reply
            original_author: t.Optional[str] = None
            original_text: t.Optional[str] = None

            if message.reply_to:
                original = await message.get_reply_message()
                if original:
                    original_author = self.get_message_author(original)
                    original_text = self.get_message_text(original)

            # log the message for debug purposes
            logging.debug(
                '%s (%s): ["%s" to "%s"] "%s" to "%s"',
                message.id,
                message_date.strftime('%Y-%m-%d %H:%M:%S'),
                message_author,
                original_author,
                message_text,
                original_text,
            )

            # make the next line for LLM
            conversation_line: str
            if original_author:
                conversation_line = f'"{message_author}" replies to "{original_author}": {message_text}'
            else:
                conversation_line = f'"{message_author}" says to everyone: {message_text}'

            # make the collection of lines
            conversation.append(conversation_line)

        return conversation

    @staticmethod
    def get_message_text(message) -> str:
        return message.text.replace('\n', ' ').replace('\r', '')

    @staticmethod
    def get_message_author(message) -> str:
        if message.sender:
            if message.sender.first_name and message.sender.last_name:
                return message.sender.first_name + ' ' + message.sender.last_name
            elif message.sender.first_name:
                return message.sender.first_name
            elif message.sender.last_name:
                return message.sender.last_name
            else:
                return str(message.sender.id)
        else:
            return 'unknown'
