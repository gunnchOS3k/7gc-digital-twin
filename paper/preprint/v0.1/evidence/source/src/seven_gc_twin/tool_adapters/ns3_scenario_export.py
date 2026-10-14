"""Export neutral stub for ns3."""
from pathlib import Path
import json

def export(site_id: str, out_dir: Path | None = None) -> Path:
    out_dir = out_dir or Path("results/tool_exports")
    out_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "site_id": site_id,
        "backend": "ns3",
        "evidence_status": "export_stub_smoke_only",
        "optional_dependency": "ns3",
        "needs_local_validation": True,
    }
    path = out_dir / f"{site_id}_ns3_site_stub.json"
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path
