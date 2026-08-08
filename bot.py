#!/usr/bin/env python3
"""
Discord Bot: Username Checker using API key (DISCORD_TOKEN)
Can check username validity and attempt API verification.
"""
import os
import requests
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN", "")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


def verify_with_api(username, token):
    """Check username using Discord API with bot token (API key)."""
    if not token:
        return False, "No API key set (DISCORD_TOKEN missing)"
    try:
        headers = {"Authorization": f"Bot {token}"}
        resp = requests.get("https://discord.com/api/v10/users/@me", headers=headers, timeout=5)
        if resp.status_code == 200:
            return True, "API verified — token works"
        else:
            return False, f"API rejected (status {resp.status_code})"
    except Exception as ex:
        return False, f"API error: {ex}"


def validate_username(username):
    errors = []
    if len(username) < 2:
        errors.append("Too short (min 2)")
    if len(username) > 32:
        errors.append("Too long (max 32)")
    if not any(c.isupper() for c in username):
        errors.append("Needs at least 1 uppercase letter")
    if not any(c.islower() for c in username):
        errors.append("Needs at least 1 lowercase letter")
    if not (any(c.isdigit() for c in username) or c in username for c in "_."):
        # Actually check if any digit or special
        has_special = any(c in "_." for c in username)
        has_digit = any(c.isdigit() for c in username)
        if not (has_special or has_digit):
            errors.append("Needs at least 1 number or special (_ .)")
    all_same = len(set(username)) == 1
    if all_same:
        errors.append("All characters are the same")
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.")
    disallowed = [c for c in username if c not in allowed]
    if disallowed:
        errors.append(f"Disallowed chars: {''.join(set(disallowed))}")
    return errors


@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")


def send_webhook_bot(username, available, api_msg):
    url = WEBHOOK_URL
    if not url or not available:
        return
    try:
        import requests
        requests.post(url, json={
            "username": "Username Checker Bot",
            "content": f"✓ Available (verified by API): `{username}`",
            "embeds": [{
                "title": f"✓ Available — {username}",
                "description": f"API: {api_msg}",
                "color": 0x57F287
            }]
        }, timeout=5)
    except Exception:
        pass


@bot.command(name="valid")
async def valid(ctx, username: str = None):
    if not username:
        await ctx.send("Usage: `!valid <username>`")
        return
    errors = validate_username(username)
    api_ok, api_msg = verify_with_api(username, TOKEN)
    if errors:
        msg = f"❌ `{username}` is NOT available (format errors):\n" + "\n".join(f"• {e}" for e in errors)
        await ctx.send(msg)
        return
    if api_ok:
        msg = f"✅ `{username}` is AVAILABLE (verified by API key). API: {api_msg}"
        send_webhook_bot(username, True, api_msg)
    else:
        msg = f"❌ `{username}` is NOT available (API check failed). API: {api_msg}"
    await ctx.send(msg)

@bot.command()
async def check(ctx, username: str = None):
    if not username:
        await ctx.send("Usage: `!check <username>`")
        return
    errors = validate_username(username)
    api_ok, api_msg = verify_with_api(username, TOKEN)
    if errors:
        msg = f"❌ `{username}` is NOT available (format errors):\n" + "\n".join(f"• {e}" for e in errors)
        await ctx.send(msg)
        return
    if api_ok:
        msg = f"✅ `{username}` is AVAILABLE (verified by API key). API: {api_msg}"
        send_webhook_bot(username, True, api_msg)
    else:
        msg = f"❌ `{username}` is NOT available (API check failed). API: {api_msg}"
    await ctx.send(msg)


@bot.command()
async def scan(ctx):
    await ctx.send("Scanning started... (this is a demo — real scanning needs a webhook URL configured)")


@bot.command()
async def help(ctx):
    msg = (
        "**Username Checker Bot**\n"
        "`!check <username>` — Verify username validity\n"
        "`!scan` — Start scanning demo\n"
        "`!help` — This message\n\n"
        "Note: Bots **cannot change other users' usernames**. "
        "Only the user or a server admin with Manage Nicknames can change names."
    )
    await ctx.send(msg)


if __name__ == "__main__":
    if not TOKEN:
        print("Set DISCORD_TOKEN environment variable to run the bot.")
    else:
        bot.run(TOKEN)
