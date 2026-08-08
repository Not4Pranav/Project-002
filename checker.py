#!/usr/bin/env python3
"""
Discord Username Checker
Checks usernames against configurable rules.
"""
import json
import random
import string


def load_config(path="config.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def check_username(username, config):
    errors = []
    min_len = config.get("min_length", 3)
    max_len = config.get("max_length", 32)
    min_letters = config.get("min_letters", 0)
    max_letters = config.get("max_letters", 32)
    min_numbers = config.get("min_numbers", 0)
    max_numbers = config.get("max_numbers", 32)
    allowed_special = config.get("allowed_special_chars", "")
    require_mixed_case = config.get("require_mixed_case", False)

    if len(username) < min_len:
        errors.append(f"Length {len(username)} < min {min_len}")
    if len(username) > max_len:
        errors.append(f"Length {len(username)} > max {max_len}")

    letters = sum(1 for c in username if c.isalpha())
    numbers = sum(1 for c in username if c.isdigit())
    specials = sum(1 for c in username if c in allowed_special)

    if letters < min_letters:
        errors.append(f"Letters {letters} < min {min_letters}")
    if letters > max_letters:
        errors.append(f"Letters {letters} > max {max_letters}")
    if numbers < min_numbers:
        errors.append(f"Numbers {numbers} < min {min_numbers}")
    if numbers > max_numbers:
        errors.append(f"Numbers {numbers} > max {max_numbers}")

    allowed_chars = set(string.ascii_letters + string.digits + allowed_special)
    disallowed = [c for c in username if c not in allowed_chars]
    if disallowed:
        errors.append(f"Disallowed chars: {''.join(set(disallowed))}")

    if require_mixed_case:
        has_lower = any(c.islower() for c in username)
        has_upper = any(c.isupper() for c in username)
        if not (has_lower and has_upper):
            errors.append("Mixed case required (lower + upper)")

    passed = len(errors) == 0
    return {
        "username": username,
        "passed": passed,
        "errors": errors,
        "stats": {
            "letters": letters,
            "numbers": numbers,
            "specials": specials,
            "length": len(username)
        }
    }
