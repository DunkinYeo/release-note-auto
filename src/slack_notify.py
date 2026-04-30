import requests


def notify_slack(
    token: str,
    channel: str,
    product_name: str,
    version: str,
    date: str,
    product_type: str,
    new_functionalities: list = None,
    change_categories: list = None,
    enhancements: list = None,
    webhook_url: str = "",
    artifact_url: str = "",
):
    blocks = _build_blocks(product_name, version, date, product_type,
                           new_functionalities, change_categories, enhancements,
                           artifact_url=artifact_url)

    if token and channel:
        r = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {token}"},
            json={"channel": channel, "blocks": blocks,
                  "text": f"{product_name} {version} Release Notes"},
            timeout=15,
        )
        if not r.json().get("ok"):
            print("Slack chat.postMessage failed:", r.json().get("error"))
        else:
            print("Slack message posted.")
    elif webhook_url:
        r = requests.post(webhook_url, json={"blocks": blocks}, timeout=15)
        if not r.ok:
            print("Slack webhook failed:", r.status_code)
        else:
            print("Slack webhook posted.")


def _build_blocks(product_name, version, date, product_type,
                  new_functionalities, change_categories, enhancements,
                  artifact_url: str = ""):
    label = f"{product_name} {product_type.upper()} {version}"
    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"📋 {label} Release Notes"},
        },
        {
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": f"📅 {date}"}],
        },
        {"type": "divider"},
    ]

    if new_functionalities:
        items = "\n".join(f"• {i}" for i in new_functionalities)
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*✨ New Functionalities*\n{items}"},
        })
        blocks.append({"type": "divider"})

    if change_categories:
        for cat in change_categories:
            title = cat.get("title", "")
            items = cat.get("items", [])
            body = "\n".join(f"• {i}" for i in items)
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*{title}*\n{body}"},
            })
            blocks.append({"type": "divider"})
    elif enhancements:
        items = "\n".join(f"• {i}" for i in enhancements)
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Enhancements*\n{items}"},
        })
        blocks.append({"type": "divider"})

    if artifact_url:
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "📥 PDF 다운로드"},
                    "style": "primary",
                    "url": artifact_url,
                }
            ],
        })

    return blocks


# Legacy function kept for backward compatibility
def notify_webhook(webhook_url: str, message: str, pdf_path: str, png_path: str,
                   token: str = "", channel: str = ""):
    payload = {"text": message}
    try:
        r = requests.post(webhook_url, json=payload, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print("Slack webhook notify failed:", e)
