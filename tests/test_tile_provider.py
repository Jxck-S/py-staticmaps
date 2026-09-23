"""py-staticmaps - Test TileProvider"""

# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

# pylint: disable=protected-access

import inspect
import math
import re

import pytest  # type: ignore
from packaging.version import Version  # type: ignore

import staticmaps
from staticmaps import meta, tile_provider
from staticmaps.tile_downloader import TileDownloader, redact_url
from staticmaps.transformer import Transformer


def test_sharding() -> None:
    t = staticmaps.TileProvider(name="test", url_pattern="$s/$z/$x/$y", shards=["0", "1", "2"])
    shard_counts = [0, 0, 0]
    for x in range(0, 100):
        for y in range(0, 100):
            u = t.url(0, x, y)
            for s in [0, 1, 2]:
                if u == f"{s}/0/{x}/{y}":
                    shard_counts[s] += 1
    assert shard_counts[0] + shard_counts[1] + shard_counts[2] == 100 * 100
    third = (100 * 100) // 3
    for s in shard_counts:
        assert (third * 0.9) < s
        assert s < (third * 1.1)


def test_tile_provider_init() -> None:
    t1 = staticmaps.tile_provider_JawgLight
    t1.set_api_key("0123456789876543210")

    t2 = staticmaps.TileProvider(
        "jawg-light",
        url_pattern="https://$s.tile.jawg.io/jawg-light/$z/$x/$y.png",
        shards=["a", "b", "c", "d"],
        attribution="Maps (C) Jawg Maps (C) OpenStreetMap.org contributors",
        max_zoom=20,
        api_key="0123456789876543210",
        key_param="access-token",
        requires_key=True,
    )
    assert t1.name() == t2.name() == "jawg-light"
    assert t1.attribution() == t2.attribution() == "Maps (C) Jawg Maps (C) OpenStreetMap.org contributors"
    assert t1.tile_size() == t2.tile_size() == 256
    # both declare more, but TileProvider still clamps every provider to 20
    assert t1.max_zoom() == t2.max_zoom() == 20
    assert t1.url(1, 2, 3) == t2.url(1, 2, 3)


def test_every_provider_is_exported() -> None:
    """Providers have gone missing from the top-level exports before while
    still being reachable through default_tile_providers, so check the whole
    module rather than a hand-written list."""
    defined = re.findall(r"^(tile_provider_\w+) = TileProvider\(", inspect.getsource(tile_provider), re.M)
    assert len(defined) > 15
    for name in defined:
        assert name in staticmaps.__all__, f"{name} is not exported"
        assert hasattr(staticmaps, name)


def test_registry_is_keyed_by_provider_name() -> None:
    for name, provider in staticmaps.default_tile_providers.items():
        assert provider.name() == name


def test_stadia_light_and_dark_are_distinct() -> None:
    """Both were constructed with the same name, so the registry kept only one
    and the two would have shared a cache directory."""
    light = staticmaps.tile_provider_StadiaAlidadeSmooth
    dark = staticmaps.tile_provider_StadiaAlidadeSmoothDark
    assert light.name() != dark.name()
    assert staticmaps.default_tile_providers[light.name()] is light
    assert staticmaps.default_tile_providers[dark.name()] is dark


def test_key_param_is_per_provider() -> None:
    """Providers agree on a query parameter and disagree on its name."""
    assert staticmaps.tile_provider_Carto.key_param() == "key"
    assert staticmaps.tile_provider_StadiaAlidadeSmooth.key_param() == "api_key"
    assert staticmaps.tile_provider_JawgLight.key_param() == "access-token"
    assert staticmaps.tile_provider_OSM.key_param() is None
    assert staticmaps.tile_provider_OSM.requires_key() is False


def test_key_is_appended_with_the_right_separator() -> None:
    p = staticmaps.TileProvider("t", url_pattern="https://x/$z/$x/$y.png", key_param="key", api_key="K")
    assert p.url(1, 2, 3) == "https://x/1/2/3.png?key=K"

    q = staticmaps.TileProvider("q", url_pattern="https://x/$z/$x/$y.png?s=a", key_param="key", api_key="K")
    assert q.url(1, 2, 3) == "https://x/1/2/3.png?s=a&key=K"


def test_key_is_url_escaped() -> None:
    p = staticmaps.TileProvider("t", url_pattern="https://x/$z/$x/$y.png", key_param="key", api_key="a b&c=d")
    assert p.url(1, 2, 3) == "https://x/1/2/3.png?key=a%20b%26c%3Dd"


def test_missing_required_key_raises() -> None:
    """Carto answers 200 with a watermarked tile when the key is absent, so a
    silent pass here produces a ruined map with no error anywhere."""
    p = staticmaps.tile_provider_Carto
    assert p.requires_key()
    with pytest.raises(ValueError):
        p.url(14, 2621, 6333)

    p2 = staticmaps.TileProvider("t", url_pattern="https://x/$z/$x/$y.png", key_param="key", requires_key=True)
    with pytest.raises(ValueError):
        p2.url(1, 2, 3)
    p2.set_api_key("K")
    assert p2.url(1, 2, 3) == "https://x/1/2/3.png?key=K"


def test_unset_legacy_key_is_not_the_string_none() -> None:
    """string.Template stringifies None, so an unset key used to be sent as
    the literal "None"."""
    p = staticmaps.TileProvider("t", url_pattern="https://x/$z/$x/$y.png?t=$k")
    assert p.url(1, 2, 3) == "https://x/1/2/3.png?t="


def test_carto_2x_providers_declare_512_tiles() -> None:
    assert staticmaps.tile_provider_Carto.tile_size() == 256
    assert staticmaps.tile_provider_Carto2x.tile_size() == 512
    assert "@2x" in staticmaps.tile_provider_Carto2x._url_pattern.template


def test_pixel_density_mirrors_the_vector_pixel_ratio() -> None:
    """Raster density comes from the tiles, vector density from the render
    call, but both mean the same thing, so both should be introspectable."""
    assert staticmaps.tile_provider_OSM.pixel_density() == 1.0
    assert staticmaps.tile_provider_Carto.pixel_density() == 1.0
    assert staticmaps.tile_provider_Carto2x.pixel_density() == 2.0


def test_a_2x_provider_covers_half_the_ground_at_a_fixed_size() -> None:
    """Switching to an "@2x" provider without changing the requested size
    trades coverage for density, exactly as pixel_ratio does for vector."""
    centre = staticmaps.create_latlng(37.799, -122.400)

    def span(tile_size: int) -> float:
        t = Transformer(1080, 1080, 15, centre, tile_size)
        return abs(t.pixel2ll(1080, 0).lng().degrees - t.pixel2ll(0, 0).lng().degrees)

    assert abs(span(256) / span(512) - 2.0) < 1e-12


def test_raster_2x_and_vector_ratio_cover_the_same_ground() -> None:
    """The equivalence the two mechanisms are supposed to share."""

    centre = staticmaps.create_latlng(37.799, -122.400)

    def span(t: Transformer, width: int) -> float:
        return abs(t.pixel2ll(width, 0).lng().degrees - t.pixel2ll(0, 0).lng().degrees)

    raster_2x = Transformer(1080, 1080, 15, centre, 512)
    vector_2x = Transformer(1080, 1080, 15 + math.log2(2), centre, 256)
    assert abs(span(raster_2x, 1080) - span(vector_2x, 1080)) < 1e-12


def test_error_messages_do_not_leak_the_api_key() -> None:
    """An api key travels in the query string, so an unredacted url in an
    exception leaks it into logs and tracebacks."""
    assert redact_url("https://x/1/1/1.png?key=SECRET") == "https://x/1/1/1.png?<redacted>"
    assert redact_url("https://x/1/1/1.png?s=a&api_key=SECRET") == "https://x/1/1/1.png?<redacted>"
    assert "SECRET" not in redact_url("https://x/1/1/1.png?access-token=SECRET")
    # a url without a query string is unchanged
    assert redact_url("https://x/1/1/1.png") == "https://x/1/1/1.png"


def test_requests_identify_this_fork() -> None:
    """The user agent is how a tile server identifies its clients and enforces
    its usage policy, so it must name the repository actually making the
    request rather than the one this was forked from."""
    agent = TileDownloader()._user_agent
    assert meta.GITHUB_URL in agent
    assert "flopp/py-staticmaps" not in agent
    assert meta.VERSION in agent


def test_version_is_distinguishable_from_upstream() -> None:
    """Both projects report py-staticmaps; only the version tells them apart."""

    assert Version(meta.VERSION) > Version("0.5.0")
    assert Version(meta.VERSION).local is not None
