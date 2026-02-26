import os
import requests


def notify_webhook(webhook_url: str, message: str, pdf_path: str, png_path: str,
                   token: str = "", channel: str = ""):
    # 1. Send text via webhook
    payload = {"text": message}
    try:
        r = requests.post(webhook_url, json=payload, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print("Slack webhook notify failed:", e)

    # 2. Upload files via Slack API (requires bot token + channel)
    if token and channel:
        for file_path in [pdf_path, png_path]:
            if os.path.isfile(file_path):
                _upload_file(token, channel, file_path)


def _upload_file(token: str, channel: str, file_path: str):
    """Upload a file to Slack using the new Files API (getUploadURLExternal)."""
    filename = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    # Step 1: Get upload URL
    try:
        r1 = requests.post(
            "https://slack.com/api/files.getUploadURLExternal",
            headers={"Authorization": f"Bearer {token}"},
            data={"filename": filename, "length": file_size},
            timeout=30,
        )
        data1 = r1.json()
        if not data1.get("ok"):
            print(f"Slack upload URL error ({filename}):", data1.get("error"))
            return
        upload_url = data1["upload_url"]
        file_id = data1["file_id"]
    except Exception as e:
        print(f"Slack upload URL request failed ({filename}):", e)
        return

    # Step 2: PUT file content to upload URL
    try:
        with open(file_path, "rb") as f:
            r2 = requests.put(upload_url, data=f, timeout=60)
        if not r2.ok:
            print(f"Slack file PUT failed ({filename}): HTTP {r2.status_code}")
            return
    except Exception as e:
        print(f"Slack file PUT error ({filename}):", e)
        return

    # Step 3: Complete upload and share to channel
    try:
        r3 = requests.post(
            "https://slack.com/api/files.completeUploadExternal",
            headers={"Authorization": f"Bearer {token}"},
            json={"files": [{"id": file_id}], "channel_id": channel},
            timeout=30,
        )
        data3 = r3.json()
        if not data3.get("ok"):
            print(f"Slack complete upload error ({filename}):", data3.get("error"))
        else:
            print(f"Slack file uploaded: {filename}")
    except Exception as e:
        print(f"Slack complete upload request failed ({filename}):", e)
