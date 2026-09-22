"""py-staticmaps - tests for vector tile providers"""

# _resolve_size is exercised directly so every size rule can be tested
# without a network round trip.
# pylint: disable=protected-access

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


def _ctx(provider: staticmaps.TileProvider) -> staticmaps.Context:
    c = staticmaps.Context()
    c.set_tile_provider(provider)
    c.set_center(staticmaps.create_latlng(37.7990, -122.4000))
    c.set_zoom(14)
    return c


def test_size_is_the_resulting_image() -> None:
    """size names the image you get; logical_size names what the ratio is
    applied to. Both reach 1080 here, by different routes."""
    p = staticmaps.VectorTileProvider("test", style=STYLE)
    assert _ctx(p)._resolve_size(None, None, (1080, 1080), None, None) == (1080, 1080, 1.0)
    assert _ctx(p)._resolve_size(None, None, (1080, 1080), None, 2) == (540, 540, 2)
    assert _ctx(p)._resolve_size(None, None, None, (540, 540), 2) == (540, 540, 2)


def test_legacy_width_height_still_works() -> None:
    p = staticmaps.VectorTileProvider("test", style=STYLE)
    assert _ctx(p)._resolve_size(800, 600, None, None, None) == (800, 600, 1.0)


def test_raster_forces_ratio_to_one() -> None:
    c = _ctx(staticmaps.tile_provider_OSM)
    c.set_pixel_ratio(2)
    assert c._resolve_size(None, None, (800, 600), None, None) == (800, 600, 1.0)


def test_size_conflicts_are_rejected() -> None:
    c = _ctx(staticmaps.VectorTileProvider("test", style=STYLE))
    with pytest.raises(ValueError):
        c._resolve_size(None, None, (1, 1), (1, 1), None)
    with pytest.raises(ValueError):
        c._resolve_size(800, 600, (1, 1), None, None)
    with pytest.raises(ValueError):
        c._resolve_size(None, None, None, None, None)
    with pytest.raises(ValueError):
        c._resolve_size(800, None, None, None, None)
    with pytest.raises(ValueError):
        c._resolve_size(None, None, (0, 100), None, None)


def test_explicit_ratio_on_raster_raises() -> None:
    """Silently ignoring it would make an OSM map come out at the wrong size
    with no explanation."""
    c = _ctx(staticmaps.tile_provider_OSM)
    with pytest.raises(ValueError):
        c._resolve_size(None, None, (800, 600), None, 2)
