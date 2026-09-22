"""py-staticmaps - tests for vector tile providers"""

# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import json

import pytest  # type: ignore

import staticmaps
from staticmaps.vector_tile_provider import _strip_html

STYLE = {
    "version": 8,
    "sources": {},
    "layers": [{"id": "bg", "type": "background", "paint": {"background-color": "#ffffff"}}],
}


def test_strip_html() -> None:
    assert _strip_html("<a href='x'>OpenFreeMap</a> <a>&copy; OpenMapTiles</a>") == "OpenFreeMap © OpenMapTiles"
    assert _strip_html("Maps &amp; Data &#169; test") == "Maps & Data © test"
    assert _strip_html("plain") == "plain"
    assert _strip_html("") == ""


def test_needs_a_style() -> None:
    with pytest.raises(ValueError):
        staticmaps.VectorTileProvider("broken")


def test_serves_no_raster_tiles() -> None:
    p = staticmaps.VectorTileProvider("test", style=STYLE)
    assert p.url(14, 1, 1) is None
    assert p.is_vector() is True


def test_raster_providers_are_not_vector() -> None:
    assert staticmaps.tile_provider_OSM.is_vector() is False
    assert staticmaps.tile_provider_OSM.tile_size() == 256


def test_style_accepts_dict_or_string() -> None:
    from_dict = staticmaps.VectorTileProvider("a", style=STYLE)
    from_str = staticmaps.VectorTileProvider("b", style=json.dumps(STYLE))
    assert json.loads(from_dict.style()) == json.loads(from_str.style()) == STYLE


def test_name_carries_a_version_hash() -> None:
    """The cache key must change with the style, so a rotated tile url or a
    different style does not serve stale imagery."""
    p = staticmaps.VectorTileProvider("test", style=STYLE)
    assert p.name().startswith("test-")

    # an unresolved provider has no hash yet, so it must not claim one
    unresolved = staticmaps.VectorTileProvider("test", style_url="https://example.com/style")
    assert unresolved.name() == "test"


def test_tile_size_is_per_provider() -> None:
    assert staticmaps.VectorTileProvider("a", style=STYLE).tile_size() == 256
    assert staticmaps.VectorTileProvider("b", style=STYLE, tile_size=512).tile_size() == 512


def test_presets() -> None:
    assert staticmaps.openfreemap("liberty").is_vector()
    assert "openfreemap" in staticmaps.openfreemap("liberty").name()
    assert "maptoolkit" in staticmaps.maptoolkit("dark").name()
    assert "versatiles" in staticmaps.versatiles("colorful").name()
    # 5 OpenFreeMap + 3 Maptoolkit + 5 VersaTiles
    assert len(staticmaps.default_vector_tile_providers) == 13
    assert all(p.is_vector() for p in staticmaps.default_vector_tile_providers.values())


def test_explicit_attribution_wins() -> None:
    p = staticmaps.VectorTileProvider("test", style=STYLE, attribution="mine")
    assert p.attribution() == "mine"


def test_pixel_ratio_is_vector_only() -> None:
    """A raster provider is served at a fixed density, so the ratio must not
    silently change its output size."""
    c = staticmaps.Context()
    c.set_tile_provider(staticmaps.VectorTileProvider("test", style=STYLE))
    c.set_pixel_ratio(2)
    assert c.pixel_ratio() == 2

    c.set_tile_provider(staticmaps.tile_provider_OSM)
    assert c.pixel_ratio() == 1.0


def test_bad_pixel_ratio() -> None:
    c = staticmaps.Context()
    for bad in (0, -1):
        with pytest.raises(ValueError):
            c.set_pixel_ratio(bad)
