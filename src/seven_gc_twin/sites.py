"""Load and validate 7GC site configurations."""
from pathlib import Path
import yaml

from .site_validator import validate_site

SITES_DIR = Path(__file__).resolve().parents[2] / "configs" / "sites"


def load_site(site_id: str) -> dict:
    path = SITES_DIR / f"{site_id}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Unknown site: {site_id}")
    with path.open() as f:
        data = yaml.safe_load(f)
    if data.get("site_id") != site_id:
        raise ValueError(f"site_id mismatch in {path}")
    return validate_site(data, str(path))


def list_sites() -> list[str]:
    return sorted(p.stem for p in SITES_DIR.glob("*.yaml"))
