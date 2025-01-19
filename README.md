# telegpt

## prerequisites

1. Install Conda
2. Register your own application https://core.telegram.org/api/obtaining_api_id#obtaining-api-id
3. Set environment variables

```shell
TELEGPT_APP_ID='your-app-id'
TELEGPT_APP_HASH='your-app-hash'
TELEGPT_APP_PHONE='your-account-phone-number'
TELEGPT_CHAT='chat-name'

GOOGLE_AI_KEY='access-key-to-google-gemini'
```

## init environment

```shell
make env-init
make env-create
```

## run

```shell
bin/telegpt.sh --app-id=XXX --app-hash=XXX --app-phone=XXX --chat=XXXX --date=2025-01-09
```
