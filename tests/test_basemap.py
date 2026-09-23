"""py-staticmaps - tests for basemap backends"""

# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import pytest  # type: ignore

import staticmaps
from staticmaps.basemap import MAPLIBRE_ZOOM_OFFSET


def test_maplibre_zoom_offset() -> None:
    """MapLibre GL measures zoom against 512px tiles, this library against
    256px ones. Verified against pymgl: the world fits a 512px image at zoom 0
    and a 1024px image at zoom 1."""
    assert MAPLIBRE_ZOOM_OFFSET == -1


def test_unknown_backend() -> None:
    with pytest.raises(ValueError):
        staticmaps.select_backend("nope")


def test_pymgl_backend_is_selectable_without_probing() -> None:
    backend = staticmaps.select_backend("pymgl")
    assert backend.name() == "pymgl"
