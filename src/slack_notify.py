import os
import requests

def notify_webhook(webhook_url: str, message: str, pdf_path: str, png_path: str):
    # Webhook can only send text/blocks. It can't upload files.
    # We post a concise message and leave artifacts to CI upload / shared drive.
    payload = {"text": message}
    try:
        r = requests.post(webhook_url, json=payload, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print("Slack webhook notify failed:", e)
