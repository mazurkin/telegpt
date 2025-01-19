# telegpt

## prerequisites

1. Install Conda
2. Register your own application https://core.telegram.org/api/obtaining_api_id#obtaining-api-id

## environment variables

```shell
export TELEGPT_APP_ID='your-app-id'
export TELEGPT_APP_HASH='your-app-hash'
export TELEGPT_PHONE='your-account-phone-number'
export TELEGPT_CHAT='chat-name'
```

```shell
export GOOGLE_AI_KEY='access-key-to-google-gemini'
```

## conda way

### init

```shell
make env-init
make env-create
```

### run

```shell
bin/telegpt.sh --app-id=XXX --app-hash=XXX --app-phone=XXX --chat=XXXX --date=2025-01-09
```

## docker way

```shell
make docker-build
make docker-run
```
