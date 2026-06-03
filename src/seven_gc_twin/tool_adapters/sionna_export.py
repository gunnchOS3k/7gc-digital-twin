"""Export neutral stub for sionna."""
from pathlib import Path
import json

def export(site_id: str, out_dir: Path | None = None) -> Path:
    out_dir = out_dir or Path("results/tool_exports")
    out_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "site_id": site_id,
        "backend": "sionna",
        "evidence_status": "export_stub_smoke_only",
        "optional_dependency": "sionna",
        "needs_local_validation": True,
    }
    path = out_dir / f"{site_id}_sionna_site_stub.json"
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path
