#!/usr/bin/env python3
"""
Discord Username Checker — Python CLI
Uses DISCORD_TOKEN to verify usernames via Discord API.
Only sends webhook for verified available usernames.
"""
import os
import sys
import time
import requests

TOKEN = os.getenv("DISCORD_TOKEN", "")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")


def generate_username(length=3):
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.'
    result = []
    for _ in range(length):
        result.append(chars[__import__('random').randint(0, len(chars) - 1)])
    for i in range(length - 1, 0, -1):
        j = __import__('random').randint(0, i)
        result[i], result[j] = result[j], result[i]
    return ''.join(result)


def validate(username):
    errors = []
    if len(username) < 2:
        errors.append("Too short (min 2)")
    if len(username) > 32:
        errors.append("Too long (max 32)")
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


def check_available(username):
    if not TOKEN:
        return False, "No DISCORD_TOKEN set"
    try:
        headers = {"Authorization": f"Bot {TOKEN}", "Content-Type": "application/json"}
        me = requests.get("https://discord.com/api/v10/users/@me", headers=headers, timeout=5)
        if me.status_code != 200:
            return False, f"API error getting bot info (status {me.status_code})"
        original = me.json().get("username", "")
        patch = requests.patch(
            "https://discord.com/api/v10/users/@me",
            headers=headers,
            json={"username": username},
            timeout=5
        )
        # Restore original immediately
        try:
            requests.patch(
                "https://discord.com/api/v10/users/@me",
                headers=headers,
                json={"username": original},
                timeout=5
            )
        except Exception:
            pass
        if patch.status_code == 200:
            return True, "Available (verified by briefly claiming via API)"
        else:
            data = patch.json() if patch.headers.get('content-type', '').startswith('application/json') else {}
            return False, f"Not available (status {patch.status_code}) — {data.get('message', 'username taken or invalid')}"
    except Exception as ex:
        return False, f"Exception: {ex}"


def send_webhook(username):
    url = WEBHOOK_URL
    if not url:
        return
    try:
        requests.post(url, json={
            "username": "Username Checker",
            "content": f"✓ Valid non-claimed username found: `{username}`",
            "embeds": [{
                "title": f"✓ Valid — {username}",
                "description": "Verified via API briefly claiming username.",
                "color": 0x57F287
            }]
        }, timeout=5)
    except Exception:
        pass


def main():
    import sys
    length = 3
    max_limit = 1000000
    if len(sys.argv) > 1:
        try:
            length = int(sys.argv[1])
        except ValueError:
            pass
    if len(sys.argv) > 2:
        try:
            max_limit = int(sys.argv[2])
        except ValueError:
            pass

    print(f"Starting continuous scan...")
    print(f"Characters: {length} | Max attempts: {max_limit}")
    print(f"API Key: {'set' if TOKEN else 'NOT SET'}")
    print(f"Webhook: {'configured' if WEBHOOK_URL else 'not set'}")
    print()

    attempts = 0
    scanning = True
    while scanning and attempts < max_limit:
        username = generate_username(length)
        attempts += 1
        errors = validate(username)
        if errors:
            print(f"[{attempts}] `{username}` — format errors: {', '.join(errors)}")
            continue
        available, msg = check_available(username)
        if available:
            print(f"[{attempts}] ✅ `{username}` IS AVAILABLE — {msg}")
            send_webhook(username)
        else:
            print(f"[{attempts}] ❌ `{username}` NOT AVAILABLE — {msg}")

    print()
    print(f"Stopped after {attempts} attempts.")


if __name__ == "__main__":
    main()
