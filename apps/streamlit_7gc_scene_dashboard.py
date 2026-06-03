"""7GC full scene dashboard — inspect results/scenes/."""
from pathlib import Path
import json
import streamlit as st

SITES = ["gary", "ghana", "guyana", "gaza", "geelong", "graham_land", "germany"]

st.set_page_config(page_title="7GC Scene Dashboard", layout="wide")
st.title("7GC Digital Twin — Scene Dashboard")
st.caption("Research prototype — smoke_test_only unless open_data_backed layers present")

site = st.selectbox("Campus", SITES)
root = Path("results/scenes") / site

if not root.exists():
    st.warning(f"Run: python -m seven_gc_twin.cli build-scene {site}")
    st.stop()

report = root / "reports" / "campus_report.md"
if report.exists():
    st.markdown(report.read_text(encoding="utf-8"))

col1, col2 = st.columns(2)
with col1:
    geo = root / "geo" / "community_anchors.geojson"
    if geo.exists():
        st.subheader("Community anchors (GeoJSON)")
        st.json(json.loads(geo.read_text(encoding="utf-8")))
with col2:
    manifest = root / "3d" / "scene_manifest.json"
    if manifest.exists():
        st.subheader("3D manifest")
        st.json(json.loads(manifest.read_text(encoding="utf-8")))

uc = root / "use_cases" / "use_case_register.md"
if uc.exists():
    st.subheader("Use cases")
    st.markdown(uc.read_text(encoding="utf-8"))

st.subheader("Evidence maturity")
st.table([{"site": s, "maturity": "Level 1 smoke / open-data prep"} for s in SITES])
