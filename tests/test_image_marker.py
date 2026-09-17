"""py-staticmaps - Test ImageMarker"""

# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import pytest

import staticmaps


def test_bounds_normalizes_latlng() -> None:
    """An out-of-range longitude must be normalized, as Line and Bounds already do.

    Geodesic interpolation with LONG_UNROLL emits longitudes beyond +/-180 when a
    path crosses the antimeridian. Before normalizing, bounds() raised an
    AssertionError from s2sphere for such a coordinate.
    """
    marker = staticmaps.ImageMarker(staticmaps.create_latlng(22.3, 190.0), b"", 0, 0)

    # 190 deg E is the same place as 170 deg W
    assert marker.latlng().lng().degrees == pytest.approx(-170.0)
    assert marker.bounds().is_point()


def test_bounds_leaves_in_range_latlng_alone() -> None:
    marker = staticmaps.ImageMarker(staticmaps.create_latlng(40.641766, -73.780968), b"", 0, 0)
    assert marker.latlng().lat().degrees == 40.641766
    assert marker.latlng().lng().degrees == -73.780968
    assert marker.bounds().is_point()
