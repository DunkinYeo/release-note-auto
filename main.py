import os
import datetime
import yaml

from src.git_tools import detect_tags, parse_tag, collect_commit_subjects
from src.release_note import build_release_note_pdf
from src.screenshot import pdf_to_png
from src.slack_notify import notify_webhook

ROOT = os.path.dirname(os.path.abspath(__file__))

def load_config():
    cfg_path = os.path.join(ROOT, "config", "release_config.yaml")
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def ensure_output_dirs():
    os.makedirs(os.path.join(ROOT, "output", "pdf"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "output", "screenshot"), exist_ok=True)

def main():
    ensure_output_dirs()
    cfg = load_config()

    # Date
    date_str = (cfg.get("date") or "").strip()
    if not date_str:
        date_str = datetime.date.today().strftime("%B %d, %Y")

    # Tag + range
    tag = (cfg.get("tag") or "").strip() or None
    latest_tag, prev_tag = detect_tags(tag_override=tag)
    parsed = parse_tag(latest_tag)

    # Config overrides parsed tag values when explicitly set
    product_type = (cfg.get("product_type") or "").strip() or parsed["product_type"]
    product_name = (cfg.get("product_name") or "").strip() or parsed["product_name"]
    platform     = (cfg.get("platform")     or "").strip() or parsed["platform"]
    version      = (cfg.get("version")      or "").strip() or parsed["version"]

    # Collect commits between tags (if prev exists)
    commits = collect_commit_subjects(prev_tag, latest_tag)

    # Merge content: config items + derived commits (append under Enhancements)
    new_funcs = cfg.get("new_functionalities") or []
    enhancements = cfg.get("enhancements") or []
    if commits:
        enhancements = enhancements + [f"(Git) {c}" for c in commits]

    previous_versions = cfg.get("previous_versions") or []
    contact = cfg.get("contact") or {}
    slack_cfg = cfg.get("slack") or {}

    # Build output filename from product info
    parts = [product_name.replace(" ", "_"), platform, product_type.upper(), version, "Release_Notes"]
    base = "_".join(p for p in parts if p)
    out_pdf = os.path.join(ROOT, "output", "pdf", f"{base}.pdf")
    out_png = os.path.join(ROOT, "output", "screenshot", f"{base}.png")

    build_release_note_pdf(
        pdf_path=out_pdf,
        platform=platform,
        version=version,
        date=date_str,
        new_functionalities=new_funcs,
        enhancements=enhancements,
        previous_versions=previous_versions,
        contact=contact,
        product_type=product_type,
        product_name=product_name,
    )

    pdf_to_png(out_pdf, out_png, dpi=300)

    if bool(slack_cfg.get("enabled")) and slack_cfg.get("webhook_url"):
        note = slack_cfg.get("channel_note", "")
        label = f"{product_name} {platform} {product_type.upper()} {version}".strip()
        msg = f"✅ {label} Release Notes generated ({date_str})." + (f" [{note}]" if note else "")
        notify_webhook(slack_cfg["webhook_url"], msg, out_pdf, out_png)

    print("Done:")
    print(" PDF:", out_pdf)
    print(" PNG:", out_png)

if __name__ == "__main__":
    main()
