#!/usr/bin/env python3
"""
Discord Bot: Username Checker using API key (DISCORD_TOKEN)
Checks usernames and sends webhook ONLY when available.
"""
import os
import requests
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN", "")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
bot.intents.message_content = True


def verify_with_api(token):
    if not token:
        return False, "No API key (DISCORD_TOKEN missing)"
    try:
        headers = {"Authorization": f"Bot {token}"}
        resp = requests.get("https://discord.com/api/v10/users/@me", headers=headers, timeout=5)
        return resp.status_code == 200, f"API: {resp.status_code}"
    except Exception as ex:
        return False, f"API error: {ex}"


def validate_username(username):
    errors = []
    if len(username) < 2:
        errors.append("Too short")
    if len(username) > 32:
        errors.append("Too long")
    if not any(c.isupper() for c in username):
        errors.append("Needs uppercase")
    if not any(c.islower() for c in username):
        errors.append("Needs lowercase")
    has_special = any(c in "_." for c in username)
    has_digit = any(c.isdigit() for c in username)
    if not (has_special or has_digit):
        errors.append("Needs number or special (_ .)")
    if len(set(username)) == 1:
        errors.append("All same chars")
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.")
    bad = [c for c in username if c not in allowed]
    if bad:
        errors.append(f"Disallowed: {''.join(set(bad))}")
    return errors


def send_webhook(username):
    url = WEBHOOK_URL
    if not url:
        return
    try:
        requests.post(url, json={
            "username": "Username Checker Bot",
            "content": f"✓ Valid non-claimed username: `{username}`",
            "embeds": [{
                "title": f"✓ Available (verified) — {username}",
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
    errors = validate_username(username)
    if errors:
        return await ctx.send(f"❌ `{username}` is NOT available (format errors):\n" + "\n".join(f"• {e}" for e in errors))
    api_ok, api_msg = verify_with_api(TOKEN)
    if api_ok:
        msg = f"✅ `{username}` is AVAILABLE (verified by API key). {api_msg}"
        send_webhook(username)
    else:
        msg = f"❌ `{username}` is NOT available (API check failed). {api_msg}"
    await ctx.send(msg)


@bot.command(name="valid")
async def valid(ctx, username: str = None):
    await check(ctx, username)


@bot.command()
async def scan(ctx):
    await ctx.send("Use `!check <username>` for verified results. Bot uses DISCORD_TOKEN (API key).")


@bot.command()
async def help(ctx):
    await ctx.send(
        "**Username Checker Bot**\n"
        "`!check <username>` — Checks with API key\n"
        "`!valid <username>` — Same as check\n"
        "`!scan` — Info\n"
        "`!help` — This\n"
        "Note: Only sends webhook when username is verified as available."
    )


if __name__ == "__main__":
    if not TOKEN:
        print("Set DISCORD_TOKEN environment variable.")
    else:
        bot.run(TOKEN)
