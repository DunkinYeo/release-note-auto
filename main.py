import os
import datetime
import argparse
import yaml

from src.git_tools import detect_tags, parse_tag, collect_commit_subjects
from src.release_note import build_release_note_pdf
from src.screenshot import pdf_to_png
from src.slack_notify import notify_webhook

ROOT = os.path.dirname(os.path.abspath(__file__))

def parse_args():
    p = argparse.ArgumentParser(description="Generate Wellysis Release Notes")
    p.add_argument("--tag",          default="", help="Tag override (e.g. ios-sdk-2.1.7)")
    p.add_argument("--platform",     default="", help="Platform override (iOS / Android)")
    p.add_argument("--version",      default="", help="Version override (e.g. 2.1.7)")
    p.add_argument("--product-type", default="", dest="product_type", help="sdk | app | fw")
    p.add_argument("--product-name", default="", dest="product_name", help="Display name (e.g. 'S-patch Ex')")
    return p.parse_args()

def load_config():
    cfg_path = os.path.join(ROOT, "config", "release_config.yaml")
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def ensure_output_dirs():
    os.makedirs(os.path.join(ROOT, "output", "pdf"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "output", "screenshot"), exist_ok=True)

def main():
    args = parse_args()
    ensure_output_dirs()
    cfg = load_config()

    # Date
    date_str = (cfg.get("date") or "").strip()
    if not date_str:
        date_str = datetime.date.today().strftime("%B %d, %Y")

    # Priority: CLI args > config > tag-parsed values
    # Tag: CLI → config → auto-detect
    tag = args.tag or (cfg.get("tag") or "").strip() or None
    latest_tag, prev_tag = detect_tags(tag_override=tag)
    parsed = parse_tag(latest_tag)

    # product_type: CLI → config → tag-parsed
    cli_type = args.product_type.strip()
    cfg_type  = (cfg.get("product_type") or "").strip()
    explicit_type = cli_type or cfg_type  # any explicit declaration wins

    if explicit_type:
        product_type = explicit_type
        product_name = (args.product_name or cfg.get("product_name") or "").strip() or parsed["product_name"]
        platform     = (args.platform     or cfg.get("platform")     or "").strip()   # no tag fallback when type is explicit
        version      = (args.version      or cfg.get("version")      or "").strip() or parsed["version"]
    else:
        product_type = parsed["product_type"]
        product_name = (args.product_name or cfg.get("product_name") or "").strip() or parsed["product_name"]
        platform     = (args.platform     or cfg.get("platform")     or "").strip() or parsed["platform"]
        version      = (args.version      or cfg.get("version")      or "").strip() or parsed["version"]

    # Safety guard: fail explicitly on unrecognized tag when no override is set
    if product_type == "unknown":
        print(f"ERROR: Tag '{latest_tag}' does not match any known convention.")
        print("  SDK : ios-sdk-2.1.6   /  android-sdk-2.1.6")
        print("  App : spatchex-ios-1.6.8  /  spatchex-android-1.6.8")
        print("  FW  : fw-2.4.6")
        print("Set product_type explicitly in config/release_config.yaml to override.")
        import sys; sys.exit(1)

    # Safety guard: FW has no platform
    if product_type.lower() == "fw":
        platform = ""

    # Content from config only
    new_funcs = cfg.get("new_functionalities") or []
    enhancements = cfg.get("enhancements") or []

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
        notify_webhook(
            slack_cfg["webhook_url"], msg, out_pdf, out_png,
            token=slack_cfg.get("token", ""),
            channel=slack_cfg.get("channel", ""),
        )

    print("Done:")
    print(" PDF:", out_pdf)
    print(" PNG:", out_png)

if __name__ == "__main__":
    main()
