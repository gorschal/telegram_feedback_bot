# telegram_feedback_bot

A Telegram feedback/support bot built with [aiogram](https://docs.aiogram.dev) 3.x.
It connects end users with an operator (administrator) through a dedicated support chat:
users write in a private chat with the bot, and their messages are forwarded to the
administrator's chat. The administrator replies by replying to the forwarded message,
and the reply is delivered back to the original user.

## Overview

- **Framework:** aiogram 3.21+
- **Runtime:** Python 3.12
- **Dependency management:** [uv](https://docs.astral.sh/uv/)
- **Transport:** polling (development) or webhook + aiohttp (production)
- **Configuration:** environment variables via [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

## Features

### User ↔ Administrator message flow

- A user sends a message in a private chat with the bot.
- The message is forwarded to `ADMIN_CHAT_ID` (a user, group, or channel) with a
  `#id<user_id>` hashtag appended, e.g. `#id12345`.
- The administrator replies to that forwarded message. The bot parses the trailing
  `#id<user_id>` hashtag and delivers the reply to the user via `message.copy_to(user_id)`.
- A short "Message sent!" confirmation is shown to the user and can be auto-deleted
  (see `REMOVE_SENT_CONFIRMATION`).

### Supported content types

User messages of the following types are forwarded:

- Text
- Photo
- Video
- Audio
- Voice
- Document / Animation

Other content types (stickers, locations, contacts, polls, etc.) are rejected with a
"This message type is not supported" notice. If the administrator attempts to reply
with an unsupported type such as a poll, a warning is shown in the admin chat instead.

### Commands

| Scope         | Command        | Description                                                  |
| ------------- | -------------- | ------------------------------------------------------------ |
| All users     | `/start`       | Welcome message.                                             |
| All users     | `/help`        | Brief description of supported message types.                |
| Administrator | `/who`         | Show information about the user behind a replied message.    |
| Administrator | `/ban`         | Ban a user (with notification) by replying to their message. |
| Administrator | `/shadowban`   | Shadowban a user (silent, no notification).                  |
| Administrator | `/unban`       | Remove a ban/shadowban.                                      |
| Administrator | `/list_banned` | List all banned and shadowbanned users.                      |

Ban and shadowban lists are stored **in memory** and reset on every bot restart.

### Additional behavior

- **Edited messages:** editing a previously sent message triggers a warning that the
  edit will not be delivered to the recipient.
- **Missing reply (admin):** if the administrator sends a message in the admin chat
  that is not a reply, a reminder is shown to use reply.
- **Global error handler:** unhandled exceptions are logged with full context.

## Configuration

All settings are read from environment variables (or a `.env` file).

| Variable                   | Required | Default    | Description                                                          |
| -------------------------- | -------- | ---------- | -------------------------------------------------------------------- |
| `BOT_TOKEN`                | Yes      | —          | Bot token from [@BotFather](https://t.me/botfather).                 |
| `ADMIN_CHAT_ID`            | Yes      | —          | Chat ID where messages are forwarded. Negative for groups/channels.  |
| `REMOVE_SENT_CONFIRMATION` | No       | `true`     | Auto-delete the "Message sent!" confirmation.                        |
| `DEBUG`                    | No       | `true`     | `true` → polling mode (dev); `false` → webhook mode (prod).          |
| `WEBHOOK_DOMAIN`           | No\*     | `None`     | Base domain for webhook (required when `DEBUG=false`).               |
| `WEBHOOK_PATH`             | No       | `/webhook` | Webhook URL path on the domain.                                      |
| `APP_HOST`                 | No       | `0.0.0.0`  | Interface for the aiohttp webhook server.                            |
| `APP_PORT`                 | No       | `9000`     | Port for the aiohttp webhook server.                                 |
| `CUSTOM_BOT_API`           | No       | `None`     | Custom Bot API server URL (enables local Bot API mode).              |
| `PROXY`                    | No       | `None`     | SOCKS5 proxy, e.g. `socks5://127.0.0.1:1080` (used in polling mode). |

\* `WEBHOOK_DOMAIN` is required in production (webhook) mode.

See `.env.example` for a commented template.

## Deployment

### Prerequisites

- Python 3.12 and [uv](https://docs.astral.sh/uv/getting-started/installation/), **or**
- Docker and Docker Compose.
- A bot token from [@BotFather](https://t.me/botfather).
- The chat ID of the administrator (user, group, or channel). Forward a message to
  [@my_id_bot](https://t.me/my_id_bot) to obtain it.

### 1. Local (development / polling)

```bash
# Install dependencies into a virtual environment
uv sync

# Create and fill in the environment file
cp .env.example .env
#   set BOT_TOKEN, ADMIN_CHAT_ID, and DEBUG=true

# Run the bot (polling mode)
uv run python -m src.main
```

### 2. Docker Compose (development / polling)

`docker-compose.yaml` builds the `build` stage and runs the bot in polling mode:

```bash
cp .env.example .env
#   set BOT_TOKEN, ADMIN_CHAT_ID, DEBUG=true

docker compose up --build
```

The container exposes port `9000` and uses a file-watch profile to sync source
changes during development.

### 3. Production (webhook)

For production, build the optimized `production` image and run it behind a reverse
proxy (nginx, Traefik, etc.) that terminates TLS and forwards requests to the bot's
webhook endpoint.

```bash
# .env
#   DEBUG=false
#   WEBHOOK_DOMAIN=https://feedbackbot.example.com
#   WEBHOOK_PATH=/webhook
#   APP_HOST=0.0.0.0
#   APP_PORT=9000

docker build --target production -t telegram-bot .
docker run -d --restart unless-stopped --env-file .env -p 9000:9000 telegram-bot
```

The bot will:

1. Call `set_webhook` on `WEBHOOK_DOMAIN + WEBHOOK_PATH`.
2. Start an aiohttp server on `APP_HOST:APP_PORT`.
3. Forward Telegram updates to the registered webhook path.

Ensure the reverse proxy routes `https://feedbackbot.example.com/webhook` to
`http://<container>:9000/webhook`.

### CI

The repository includes GitHub Actions workflows:

- `.github/workflows/validator.yml` — runs `ruff check`, `ruff format --check`, and `pytest`
  on pull requests to `main`.
- `.github/workflows/docker.yml` — builds and publishes a Docker image to GHCR on version tags.

## Project structure

```
src/
├── main.py                 # Entry point: polling / webhook bootstrap
├── core/
│   ├── config_reader.py    # Settings via pydantic-settings (.env)
│   ├── commands_worker.py  # Bot command registration (/ban, /who, /help...)
│   └── block_lists.py      # In-memory banned/shadowbanned storage
├── filters/
│   └── supported_media.py  # Custom filter for supported media types
├── handlers/
│   ├── user_mode.py        # User → admin forwarding
│   ├── admin_mode.py       # Admin reply → user, /who
│   ├── admin_no_reply.py   # Admin missing-reply warning
│   ├── bans.py             # Ban / shadowban / unban commands
│   ├── message_edit.py     # Edited message warning
│   ├── unsupported_reply.py# Unsupported admin reply filter
│   └── errors.py           # Global error handler
└── middlewares/            # Reserved for future middleware
```

## Testing

```bash
uv sync
uv run pytest
```

Tests use `pytest-asyncio` (auto mode) and mock the Telegram API, so no real bot
token is required — `conftest.py` provides test defaults for `BOT_TOKEN` and
`ADMIN_CHAT_ID`.
