# telegpt

The example of a command-line client for Telegram (this is not a Telegram bot).

The client fetches the history of the messages from the chat for the period
and makes the summary of conversation using LLM model.

This is my [feature request](https://bugs.telegram.org/c/44288) in the Telegram's issue tracket.

## prerequisites

1. Install Conda or Docker or both
2. Register your own Telegram client application https://core.telegram.org/api/obtaining_api_id#obtaining-api-id
3. Install the local Ollama server https://ollama.com/ and pull the required model (phi4:14b)

## environment variables

```shell
# application
export TELEGPT_APP_ID='your-app-id'
export TELEGPT_APP_HASH='your-app-hash'
````

```shell
# personal profile
export TELEGPT_PHONE='your-account-phone-number'
```

```shell
# other settings
export TELEGPT_CHAT='chat-name'
export TELEGPT_SUMMARIZER='GEMINI'
```

## conda way

### init

```shell
make env-init
make env-create
```

### run

```shell
# summary for this day
bin/telegpt.sh --chat=mychatname --prompt=example.txt --summarizer=OLLAMA

# summary for the specific day
bin/telegpt.sh --chat=mychatname --prompt=example.txt --summarizer=OLLAMA --date=2025-01-09
```

## docker way

```shell
make docker-build
make docker-run
```
