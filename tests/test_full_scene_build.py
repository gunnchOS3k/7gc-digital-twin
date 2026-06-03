import json
from pathlib import Path

import pytest

from seven_gc_twin.config.loader import list_site_ids, load_site_config
from seven_gc_twin.config.validator import validate_site_config
from seven_gc_twin.scene_builder import SITES, build_scene, build_all_scenes, make_conference_artifacts


@pytest.mark.parametrize("site_id", SITES)
def test_validate_site(site_id):
    cfg = load_site_config(site_id)
    assert validate_site_config(cfg) == []


def test_build_scene_synthetic(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    r = build_scene("gary", mode="synthetic-fixture")
    assert Path(r["report"]).exists()
    assert (Path("results/scenes/gary/3d/scene.gltf")).exists()
    data = json.loads((Path("results/scenes/gary/3d/scene.gltf")).read_text())
    assert data["asset"]["version"] == "2.0"


def test_geojson_valid(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    build_scene("ghana", mode="synthetic-fixture")
    geo = json.loads((Path("results/scenes/ghana/geo/base_layers.geojson")).read_text())
    assert geo["type"] == "FeatureCollection"


def test_sionna_xml_parseable(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    build_scene("gaza", mode="synthetic-fixture")
    import xml.etree.ElementTree as ET
    ET.parse(Path("results/scenes/gaza/3d/sionna_scene.xml"))


def test_build_all_and_conference(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert len(build_all_scenes(mode="synthetic-fixture")) == 7
    make_conference_artifacts()
    assert Path("results/conference/7gc_scene_table.md").exists()
