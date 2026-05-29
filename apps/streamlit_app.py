"""Minimal 7GC digital twin dashboard (research scaffold)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import streamlit as st
from seven_gc_twin.sites import list_sites, load_site
from seven_gc_twin.scenario_loader import load_scenario
from seven_gc_twin.visualization_stub import site_summary_table

st.set_page_config(page_title="7GC Digital Twin", layout="wide")
st.title("7GC AI-RAN Digital Twin — Research Scaffold")
st.caption("Not operational 6G infrastructure. Gary is node 1.")

site = st.selectbox("Site", list_sites())
cfg = load_site(site)
st.json(cfg)
scenario = load_scenario(site)
st.write(site_summary_table([scenario]))
