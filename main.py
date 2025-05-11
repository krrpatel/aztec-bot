import subprocess
import requests
import json
import os
import time
from datetime import datetime

CONFIG_FILE = "config.json"

def get_node_status():
    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", "-H", "Content-Type: application/json",
             "-d", '{"jsonrpc":"2.0","method":"node_getL2Tips","params":[],"id":67}',
             "http://localhost:8080"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            output = json.loads(result.stdout)
            number = output.get("result", {}).get("proven", {}).get("number")
            return number
    except Exception as e:
        print(f"[{timestamp()}] Error fetching node status: {e}")
    return None

def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"[{timestamp()}] Telegram message sent: {message}")
        else:
            print(f"[{timestamp()}] Telegram error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"[{timestamp()}] Failed to send Telegram message: {e}")
        return False

def load_or_create_config():
    if os.path.exists(CONFIG_FILE):
        use_existing = input("Found existing config. Use it? (y/n): ").strip().lower()
        if use_existing == 'y':
            with open(CONFIG_FILE, "r") as file:
                return json.load(file)

    bot_token = input("Enter your Telegram Bot API key: ").strip()
    chat_id = input("Enter your Telegram Chat ID: ").strip()
    config = {"bot_token": bot_token, "chat_id": chat_id}
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file)
    return config

def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    config = load_or_create_config()
    bot_token = config["bot_token"]
    chat_id = config["chat_id"]

    print(f"[{timestamp()}] Bot started. Checking node status every 30 minutes.")

    while True:
        number = get_node_status()
        if isinstance(number, int) and 10000 <= number <= 99999:
            message = f"Node is running fine. Block number: {number}"
        else:
            message = "Node is not running properly or returned invalid data."
        send_telegram_message(bot_token, chat_id, message)
        time.sleep(1800)  # 30 minutes

if __name__ == "__main__":
    main()
