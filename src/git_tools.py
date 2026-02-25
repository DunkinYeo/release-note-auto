import subprocess
import re
from typing import Optional, Tuple, List

TAG_RE = re.compile(r"^(?P<platform>ios|android)-sdk-(?P<version>\d+\.\d+\.\d+)$", re.IGNORECASE)

def _run(args: List[str]) -> str:
    return subprocess.check_output(args).decode("utf-8").strip()

def detect_tags(tag_override: Optional[str] = None) -> Tuple[str, Optional[str]]:
    """Return (latest_tag, previous_tag).
    If tag_override is provided, treat it as latest_tag and find previous tag before it.
    """
    if tag_override:
        latest = tag_override
        # previous tag: the tag just before this one in history (best-effort)
        try:
            prev = _run(["git", "describe", "--tags", "--abbrev=0", f"{latest}^" ])
        except Exception:
            prev = None
        return latest, prev

    latest = _run(["git", "describe", "--tags", "--abbrev=0"])  # latest reachable tag
    try:
        prev = _run(["git", "describe", "--tags", "--abbrev=0", f"{latest}^" ])
    except Exception:
        prev = None
    return latest, prev

def parse_tag(tag: str) -> Tuple[str, str]:
    """Parse tag like ios-sdk-2.1.5 into (iOS, 2.1.5)."""
    m = TAG_RE.match(tag)
    if not m:
        # fallback
        return ("iOS", tag)
    platform = m.group("platform").lower()
    version = m.group("version")
    return ("iOS" if platform == "ios" else "Android", version)

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
