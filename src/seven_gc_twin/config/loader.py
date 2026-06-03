from pathlib import Path
import yaml

PROFILES = Path(__file__).resolve().parents[3] / "configs" / "site_profiles"


def list_site_ids() -> list[str]:
    return sorted(p.stem for p in PROFILES.glob("*.yaml"))


def load_site_config(site_id: str) -> dict:
    with (PROFILES / f"{site_id}.yaml").open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    data.setdefault("scene_version", "1.0.0")
    data.setdefault("validation_status", "schema_ok")
    data.setdefault("local_partner_status", "requires_local_validation")
    data.setdefault("source_assumption_status", "mixed")
    return data
