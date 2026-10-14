"""Export neutral stub for oran_policy_loop."""
from pathlib import Path
import json

def export(site_id: str, out_dir: Path | None = None) -> Path:
    out_dir = out_dir or Path("results/tool_exports")
    out_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "site_id": site_id,
        "backend": "oran_policy_loop",
        "evidence_status": "export_stub_smoke_only",
        "optional_dependency": "oran_policy_loop",
        "needs_local_validation": True,
    }
    path = out_dir / f"{site_id}_oran_policy_loop_site_stub.json"
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path
