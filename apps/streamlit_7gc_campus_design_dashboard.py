"""Streamlit dashboard for 7GC campus design digital twin."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from site_buildings.export_bundle import export_all
from site_buildings.material_scoring import material_matrix
from site_buildings.power_model import power_model
from site_buildings.room_adjacency import build_adjacency
from site_buildings.site_registry import SITE_IDS, SITE_DISPLAY
from site_buildings.svg_floorplan_export import export_svg

st.set_page_config(page_title="7GC Campus Design Dashboard", layout="wide")
st.title("7GC Campus Design System — Digital Twin Dashboard")
st.caption("Conceptual only — not for construction | Research simulation only")

tab_names = [
    "Overview",
    "Site Selector",
    "Campus Brief",
    "Room Program",
    "Floor Plan",
    "Materials",
    "Acoustic/RF Tradeoffs",
    "Connectivity",
    "Risks",
    "Evidence Matrix",
    "Exports",
]
tabs = st.tabs(tab_names)

with tabs[0]:
    st.markdown("## WAIKE UPNOW — Seven Sites")
    st.table([{"site_id": s, "name": SITE_DISPLAY[s]} for s in SITE_IDS])

with tabs[1]:
    site = st.selectbox("Site", SITE_IDS, format_func=lambda s: SITE_DISPLAY[s])

with tabs[2]:
  try:
    site
  except NameError:
    site = SITE_IDS[0]
  st.markdown(f"### {SITE_DISPLAY[site]}")
  st.info("Host-first, not brand-first. Partner approval required for field activity.")

with tabs[3]:
  adj = build_adjacency(site)
  st.json(adj)

with tabs[4]:
  st.markdown(export_svg(site), unsafe_allow_html=True)

with tabs[5]:
  df = pd.DataFrame(material_matrix(site))
  st.dataframe(df)

with tabs[6]:
  st.markdown("**Strategy:** sound-isolated partitions + AP per zone + wired backbone")
  st.markdown("Do not rely on wall leakage for connectivity.")

with tabs[7]:
  st.json(power_model(site))

with tabs[8]:
  st.warning("All risks require expert review before construction or deployment.")

with tabs[9]:
  st.markdown("| Claim | Label |\n|-------|-------|\n| Floor plan | design assumption |\n| Materials | expert review required |")

with tabs[10]:
  if st.button("Generate exports for all sites"):
    paths = export_all(Path("results/exports"))
    st.success(f"Exported {len(paths)} sites")
    st.json({k: {kk: str(vv) for kk, vv in v.items()} for k, v in paths.items()})
