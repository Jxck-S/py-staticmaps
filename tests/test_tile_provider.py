"""py-staticmaps - Test TileProvider"""

# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import staticmaps


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
    t1 = staticmaps.tile_provider.tile_provider_JawgLight
    t1.set_api_key("0123456789876543210")

    t2 = staticmaps.TileProvider(
        "jawg-light",
        url_pattern="https://$s.tile.jawg.io/jawg-light/$z/$x/$y.png?access-token=$k",
        shards=["a", "b", "c", "d"],
        attribution="Maps (C) Jawg Maps (C) OpenStreetMap.org contributors",
        max_zoom=20,
        api_key="0123456789876543210",
    )
    assert t1.name() == t2.name() == "jawg-light"
    assert t1.attribution() == t2.attribution() == "Maps (C) Jawg Maps (C) OpenStreetMap.org contributors"
    assert t1.tile_size() == t2.tile_size() == 256
    assert t1.max_zoom() == t2.max_zoom() == 20


def test_carto_providers_are_exported() -> None:
    """All four Carto providers are in default_tile_providers and must be exported.

    tile_provider_Carto and tile_provider_CartoDark were reachable through the
    default_tile_providers dict but missing from the top-level exports, while
    their NoLabels siblings were present.
    """
    for name in (
        "tile_provider_Carto",
        "tile_provider_CartoDark",
        "tile_provider_CartoNoLabels",
        "tile_provider_CartoDarkNoLabels",
    ):
        assert name in staticmaps.__all__
        provider = getattr(staticmaps, name)
        assert staticmaps.default_tile_providers[provider.name()] is provider
