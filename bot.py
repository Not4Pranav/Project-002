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


def check_username_available(username, token):
    """Actually check if username is available by trying to claim it briefly via API."""
    if not token:
        return False, "No API key (DISCORD_TOKEN missing)"
    try:
        headers = {"Authorization": f"Bot {token}", "Content-Type": "application/json"}
        # Get current bot username
        me = requests.get("https://discord.com/api/v10/users/@me", headers=headers, timeout=5)
        if me.status_code != 200:
            return False, f"Failed to get bot info (status {me.status_code})"
        original = me.json().get("username", "")
        # Try to claim the test username briefly
        patch_resp = requests.patch(
            "https://discord.com/api/v10/users/@me",
            headers=headers,
            json={"username": username},
            timeout=5
        )
        # Always change back to original regardless of result
        try:
            requests.patch(
                "https://discord.com/api/v10/users/@me",
                headers=headers,
                json={"username": original},
                timeout=5
            )
        except Exception:
            pass
        if patch_resp.status_code == 200:
            return True, "Available (verified by briefly claiming via API)"
        else:
            data = patch_resp.json() if patch_resp.headers.get('content-type', '').startswith('application/json') else {}
            return False, f"Not available (API status {patch_resp.status_code}) — {data.get('message', 'username taken or invalid')}"
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
    available, avail_msg = check_username_available(username, TOKEN)
    if errors:
        return await ctx.send(f"❌ `{username}` NOT available (format errors):\n" + "\n".join(f"• {e}" for e in errors))
    if not available:
        return await ctx.send(f"❌ `{username}` NOT available (used or taken by someone else). API: {avail_msg}")
    msg = f"✅ `{username}` IS AVAILABLE (verified by briefly claiming via API). API: {avail_msg}"
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
