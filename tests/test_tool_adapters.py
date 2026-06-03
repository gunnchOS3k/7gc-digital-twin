import json
from pathlib import Path
from seven_gc_twin.tool_adapters.sionna_export import export

def test_sionna_export_stub(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    p = export("gary")
    assert p.exists()
    data = json.loads(p.read_text())
    assert data["evidence_status"] == "export_stub_smoke_only"
