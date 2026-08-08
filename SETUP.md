# Setup Guide

Repo: `https://github.com/Not4Pranav/Project-002`
Branch: `arena/019fe1b3-project-002`

## Quick Install
```bash
git clone https://github.com/Not4Pranav/Project-002.git
cd Project-002
git checkout arena/019fe1b3-project-002
pip install -r requirements.txt
```

## Web Dashboard (`index.html`)
- Open `index.html` in a browser (static file).
- Note: Browser CORS blocks `discord.com/api` — web checks are format-only (`format OK` / `Used`).
- For real verification, use `bot.py` or `main.py`.

## Bot (`bot.py`)
Requires `DISCORD_TOKEN` (bot token):
```bash
export DISCORD_TOKEN="your_bot_token"
python bot.py
```
Commands: `!check <username>`, `!valid <username>`, `!scan`, `!help`

Bot verifies via `PATCH /users/@me` briefly (restores original name). Reports `AVAILABLE` / `NOT AVAILABLE`.

Optional webhook (`WEBHOOK_URL`):
```bash
export WEBHOOK_URL="https://discord.com/api/webhooks/..."
```
Webhooks fire only for `available=True`.

## CLI Scanner (`main.py`)
```bash
python main.py [char_length] [max_limit]
```
Example:
```bash
python main.py 3 100000
```
Uses real `PATCH` verification. Sends webhook only for verified available.

## Flask (`app.py`)
```bash
python app.py
```
Endpoints: `/run`, `/config`.

## Config
- `index.html`: Max Limit default `1000000`; allowed chars `ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.`; buttons 1–5.
- `bot.py`: `DISCORD_TOKEN` required; `WEBHOOK_URL` optional.
- `main.py`: first arg = char length; second arg = max limit.

## GitHub Pages
Enable manually: `Settings → Pages → Source: arena/019fe1b3-project-002` → folder `/` (root).
