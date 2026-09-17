"""py-staticmaps - Test the in-memory tile cache and the user zoom range"""

# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import os
import typing

import pytest

import staticmaps
from staticmaps.tile_downloader import TileDownloader


def _cache_with_one_tile(cache_dir: str, provider: staticmaps.TileProvider) -> None:
    """Write a single fake tile into a provider's on-disk cache."""
    tile_dir = os.path.join(cache_dir, provider.name(), "5", "16")
    os.makedirs(tile_dir)
    with open(os.path.join(tile_dir, "10.png"), "wb") as handle:
        handle.write(b"FAKETILE")


def _context() -> staticmaps.Context:
    context = staticmaps.Context()
    context.set_tile_provider(staticmaps.tile_provider_None)
    context.add_object(staticmaps.Point(staticmaps.create_latlng(48.00, 8.00)))
    context.add_object(staticmaps.Point(staticmaps.create_latlng(48.01, 8.01)))
    return context


def test_loaded_tiles_starts_empty() -> None:
    assert not TileDownloader().loaded_tiles


def test_load_tiles_to_mem_populates_the_store(tmp_path: typing.Any) -> None:
    provider = staticmaps.tile_provider_OSM
    _cache_with_one_tile(str(tmp_path), provider)

    downloader = TileDownloader()
    downloader.load_tiles_to_mem(provider, 5, str(tmp_path))

    assert downloader.loaded_tiles[provider.name()][5][16][10] == b"FAKETILE"


def test_get_is_served_from_memory(tmp_path: typing.Any) -> None:
    """Once loaded, get() must not go back to disk."""
    provider = staticmaps.tile_provider_OSM
    _cache_with_one_tile(str(tmp_path), provider)

    downloader = TileDownloader()
    downloader.load_tiles_to_mem(provider, 5, str(tmp_path))

    # removing the file proves the answer came from memory
    os.remove(os.path.join(str(tmp_path), provider.name(), "5", "16", "10.png"))
    assert downloader.get(provider, str(tmp_path), 5, 16, 10) == b"FAKETILE"


def test_context_load_tiles_to_mem_needs_a_zoom() -> None:
    context = staticmaps.Context()
    with pytest.raises(ValueError):
        context.load_tiles_to_mem()


def test_zoom_in_range_clamps_both_ends() -> None:
    context = staticmaps.Context()
    context.set_max_min_zoom(6, 1)
    assert context.zoom_in_range(9) == 6
    assert context.zoom_in_range(0) == 1
    assert context.zoom_in_range(4) == 4


def test_set_max_min_zoom_bounds_the_fitted_zoom() -> None:
    unconstrained = _context()
    constrained = _context()
    constrained.set_max_min_zoom(6, 1)

    _, loose = unconstrained.determine_center_zoom(400, 400)
    _, tight = constrained.determine_center_zoom(400, 400)
    assert loose is not None and tight is not None
    assert loose > tight == 6


def test_explicit_zoom_is_not_clamped() -> None:
    """set_max_min_zoom bounds the computed zoom, not one the caller set."""
    context = _context()
    context.set_max_min_zoom(6, 1)
    context.set_zoom(12)
    assert context.determine_center_zoom(400, 400)[1] == 12


def test_set_max_min_zoom_rejects_bad_values() -> None:
    context = staticmaps.Context()
    with pytest.raises(ValueError):
        context.set_max_min_zoom(31, 1)
    with pytest.raises(ValueError):
        context.set_max_min_zoom(6, -1)


def test_reset_center_zoom_restores_fitting() -> None:
    context = _context()
    context.set_zoom(12)
    assert context.determine_center_zoom(400, 400)[1] == 12
    context.reset_center_zoom()
    assert context.determine_center_zoom(400, 400)[1] != 12
