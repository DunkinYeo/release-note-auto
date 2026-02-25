# sdk-release-automation

Generate Wellysis-style SDK Release Notes (PDF + Screenshot) from Git tags and commit messages, and optionally notify Slack.

## What it does
- Detects the latest git tag (or a given tag)
- Collects commit subjects between tags (or since the tag)
- Builds a Release Notes PDF (Android/iOS template look)
- Renders a PNG screenshot from the PDF (true PDF render)
- Optionally posts a Slack message (webhook)

## Quick start (local)
```bash
python -m venv .venv
# mac/linux
source .venv/bin/activate
# windows
# .venv\Scripts\activate

pip install -r requirements.txt

# Copy & edit config
cp config/release_config.example.yaml config/release_config.yaml

python main.py
```

Outputs:
- `output/pdf/*.pdf`
- `output/screenshot/*.png`

## Git tagging convention
Use tags like:
- `ios-sdk-2.1.5`
- `android-sdk-2.1.5`

The tool parses:
- platform = iOS/Android
- version = 2.1.5

## Slack
Two options are included:
1) Incoming Webhook (easy) — set `slack.webhook_url`
2) (Optional later) Slack file upload via bot token — not enabled by default.

## GitHub Actions (CI)
This repo includes a workflow that runs when a tag is pushed matching `ios-sdk-*` or `android-sdk-*` and uploads artifacts.

See `.github/workflows/release-notes.yml`.
