# telegpt

## prerequisites

1. Install Conda or Docker or both
2. Register your own Telegram client application https://core.telegram.org/api/obtaining_api_id#obtaining-api-id
3. Install the local Ollama server https://ollama.com/ and pull the required model (phi4:14b)

## environment variables

```shell
export TELEGPT_APP_ID='your-app-id'
export TELEGPT_APP_HASH='your-app-hash'
````

```shell
export TELEGPT_PHONE='your-account-phone-number'
export TELEGPT_CHAT='chat-name'
```

## conda way

### init

```shell
make env-init
make env-create
```

### run

```shell
bin/telegpt.sh                    # summary for this day
bin/telegpt.sh --date=2025-01-09  # summary for the specific day
```

## docker way

```shell
make docker-build
make docker-run
```
