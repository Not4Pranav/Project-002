#!/usr/bin/env python3
"""
Discord Username Checker Web Server
"""
from flask import Flask, request, jsonify
from checker import load_config, check_username

app = Flask(__name__)

@app.route("/")
def index():
    return "Discord Username Checker running. Use POST /run with JSON payload."

@app.route("/run", methods=["POST"])
def run_check():
    data = request.get_json(force=True) if request.get_json() else {}
    usernames = data.get("username_list", [])
    results = []
    for username in usernames:
        results.append(check_username(str(username), data))
    return jsonify(results)

@app.route("/config", methods=["GET"])
def get_config():
    return jsonify(load_config())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
