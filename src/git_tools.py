import subprocess
import re
from typing import Optional, Tuple, List, Dict

# sdk:      ios-sdk-2.1.6  /  android-sdk-2.1.6
_SDK_RE  = re.compile(r"^(?P<platform>ios|android)-sdk-(?P<version>[\d.]+)$", re.IGNORECASE)
# fw:       fw-2.4.6
_FW_RE   = re.compile(r"^fw-(?P<version>[\d.]+)$", re.IGNORECASE)
# app:      spatchex-ios-1.6.8  /  spatchex-android-1.6.8
#           {slug}-{platform}-{version}
_APP_RE  = re.compile(r"^(?P<slug>[a-z0-9\-]+)-(?P<platform>ios|android)-(?P<version>[\d.]+)$", re.IGNORECASE)

def _run(args: List[str]) -> str:
    return subprocess.check_output(args).decode("utf-8").strip()

def detect_tags(tag_override: Optional[str] = None) -> Tuple[str, Optional[str]]:
    """Return (latest_tag, previous_tag)."""
    if tag_override:
        latest = tag_override
        try:
            prev = _run(["git", "describe", "--tags", "--abbrev=0", f"{latest}^"])
        except Exception:
            prev = None
        return latest, prev

    latest = _run(["git", "describe", "--tags", "--abbrev=0"])
    try:
        prev = _run(["git", "describe", "--tags", "--abbrev=0", f"{latest}^"])
    except Exception:
        prev = None
    return latest, prev

def parse_tag(tag: str) -> Dict[str, str]:
    """Parse any supported tag into {product_type, product_name, platform, version}.

    Tag conventions:
      SDK:  ios-sdk-2.1.6         → sdk  / Wellysis / iOS     / 2.1.6
      FW:   fw-2.4.6              → fw   / Wellysis / (none)  / 2.4.6
      App:  spatchex-ios-1.6.8    → app  / S-patch Ex / iOS   / 1.6.8
    """
    # SDK
    m = _SDK_RE.match(tag)
    if m:
        return {
            "product_type": "sdk",
            "product_name": "Wellysis",
            "platform": "iOS" if m.group("platform").lower() == "ios" else "Android",
            "version": m.group("version"),
        }

    # Firmware
    m = _FW_RE.match(tag)
    if m:
        return {
            "product_type": "fw",
            "product_name": "Wellysis",
            "platform": "",
            "version": m.group("version"),
        }

    # App  (slug-platform-version)
    m = _APP_RE.match(tag)
    if m:
        slug = m.group("slug").lower().replace("-", "")
        # Friendly name lookup; add more as needed
        _SLUG_NAMES = {
            "spatchex": "S-patch Ex",
            "spatch":   "S-patch",
        }
        product_name = _SLUG_NAMES.get(slug, m.group("slug").title())
        return {
            "product_type": "app",
            "product_name": product_name,
            "platform": "iOS" if m.group("platform").lower() == "ios" else "Android",
            "version": m.group("version"),
        }

    # Fallback — treat as SDK
    return {
        "product_type": "sdk",
        "product_name": "Wellysis",
        "platform": "iOS",
        "version": tag,
    }

def collect_commit_subjects(prev_tag: Optional[str], latest_tag: str, max_items: int = 20) -> List[str]:
    """Collect commit subjects between prev_tag..latest_tag. If prev_tag missing, use latest_tag~20..latest_tag."""
    try:
        if prev_tag:
            rng = f"{prev_tag}..{latest_tag}"
        else:
            rng = f"{latest_tag}~{max_items}..{latest_tag}"
        out = _run(["git", "log", rng, "--pretty=format:%s"]).splitlines()
        out = [s.strip() for s in out if s.strip()]
        # de-dup while keeping order
        seen = set()
        uniq = []
        for s in out:
            if s not in seen:
                seen.add(s)
                uniq.append(s)
        return uniq[:max_items]
    except Exception:
        return []
