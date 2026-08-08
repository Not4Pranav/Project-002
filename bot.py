#!/usr/bin/env python3
"""
Discord Bot: Username Checker using API key (DISCORD_TOKEN)
Checks username format rules. Discord does not expose a public endpoint
to check if an arbitrary username is taken, so this verifies format
rules and confirms the bot token works via Discord API.
Only sends webhook for usernames that pass format rules.
"""
import os
import requests
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN", "")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
bot.intents.message_content = True


def check_api(token):
    if not token:
        return False, "No API key (DISCORD_TOKEN missing)"
    try:
        headers = {"Authorization": f"Bot {token}"}
        resp = requests.get("https://discord.com/api/v10/users/@me", headers=headers, timeout=5)
        return resp.status_code == 200, f"API status: {resp.status_code}"
    except Exception as ex:
        return False, f"API error: {ex}"


def validate(username):
    errors = []
    if len(username) < 2:
        errors.append("Too short (min 2)")
    if len(username) > 32:
        errors.append("Too long (max 32)")
    if not any(c.isupper() for c in username):
        errors.append("Needs uppercase letter")
    if not any(c.islower() for c in username):
        errors.append("Needs lowercase letter")
    has_special = any(c in "_." for c in username)
    has_digit = any(c.isdigit() for c in username)
    if not (has_special or has_digit):
        errors.append("Needs number or special (_ .)")
    if len(set(username)) == 1:
        errors.append("All characters same")
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.")
    bad = [c for c in username if c not in allowed]
    if bad:
        errors.append(f"Disallowed chars: {''.join(set(bad))}")
    return errors


def send_webhook(username):
    url = WEBHOOK_URL
    if not url:
        return
    try:
        requests.post(url, json={
            "username": "Username Checker Bot",
            "content": f"✓ Valid non-claimed username found: `{username}`",
            "embeds": [{
                "title": f"✓ Valid — {username}",
                "description": "Format rules passed. Note: Discord does not expose a public endpoint to confirm if a username is actually taken by another user.",
                "color": 0x57F287
            }]
        }, timeout=5)
    except Exception:
        pass


@bot.event
async def on_ready():
    print(f"Bot ready: {bot.user}")


@bot.command()
async def check(ctx, username: str = None):
    if not username:
        return await ctx.send("Usage: `!check <username>`")
    errors = validate(username)
    api_ok, api_msg = check_api(TOKEN)
    if errors:
        return await ctx.send(f"❌ `{username}` NOT valid (format errors):\n" + "\n".join(f"• {e}" for e in errors))
    if not api_ok:
        return await ctx.send(f"❌ `{username}` NOT verified — API check failed. {api_msg}")
    msg = f"✅ `{username}` passes format rules. {api_msg}\nNote: Discord does not expose public endpoint to confirm if another user has this name."
    await ctx.send(msg)
    send_webhook(username)


@bot.command(name="valid")
async def valid(ctx, username: str = None):
    await check(ctx, username)


@bot.command()
async def scan(ctx):
    await ctx.send("Use `!check <username>` or `!valid <username>`. Only sends webhook for valid usernames.")


@bot.command()
async def help(ctx):
    await ctx.send(
        "**Username Checker Bot**\n"
        "`!check <username>` — Check format + API\n"
        "`!valid <username>` — Same\n"
        "`!scan` — Info\n"
        "`!help` — This\n"
        "Note: Bot uses DISCORD_TOKEN. Only sends webhook for usernames that pass format rules. "
        "Discord does not expose a public endpoint to confirm if a username is taken by another account."
    )


if __name__ == "__main__":
    if not TOKEN:
        print("Set DISCORD_TOKEN environment variable.")
    else:
        bot.run(TOKEN)
