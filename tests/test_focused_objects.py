"""py-staticmaps - Test focused objects"""

# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import pytest

import staticmaps


def _context() -> staticmaps.Context:
    """A long line across Europe plus two nearby points marked as focused."""
    context = staticmaps.Context()
    context.set_tile_provider(staticmaps.tile_provider_None)
    context.add_object(staticmaps.Line([staticmaps.create_latlng(40, -5), staticmaps.create_latlng(55, 20)]))
    context.add_object(staticmaps.Point(staticmaps.create_latlng(48.0, 8.0)), focused=True)
    context.add_object(staticmaps.Point(staticmaps.create_latlng(48.1, 8.1)), focused=True)
    return context


def test_add_object_defaults_to_unfocused() -> None:
    context = staticmaps.Context()
    context.add_object(staticmaps.Point(staticmaps.create_latlng(48, 8)))
    assert context.object_bounds(focused_only=True) is None
    assert context.object_bounds() is not None


def test_object_bounds_focused_is_tighter() -> None:
    context = _context()
    everything = context.object_bounds()
    focused = context.object_bounds(focused_only=True)
    assert everything is not None and focused is not None
    assert focused.area() < everything.area()


def test_focused_only_zooms_in() -> None:
    """Fitting to the focused objects alone must zoom in further."""
    context = _context()
    _, zoom_all = context.determine_center_zoom(400, 400, False)
    _, zoom_focused = context.determine_center_zoom(400, 400, True)
    assert zoom_all is not None and zoom_focused is not None
    assert zoom_focused > zoom_all


def test_set_focused_only_drives_rendering() -> None:
    off = _context()
    on = _context()
    on.set_focused_only(True)
    assert off.focused_only() is False
    assert on.focused_only() is True
    assert list(off.render_pillow(200, 200).convert("RGB").get_flattened_data()) != list(
        on.render_pillow(200, 200).convert("RGB").get_flattened_data()
    )


def test_reset_focused_objects_keeps_objects_on_the_map() -> None:
    context = _context()
    before = context.object_bounds()
    context.reset_focused_objects()
    assert context.object_bounds(focused_only=True) is None
    assert context.object_bounds() == before


def test_remove_latest_object_also_unfocuses() -> None:
    """Removing an object must not leave a stale entry in the focused list."""
    context = _context()
    assert context.object_bounds(focused_only=True) is not None
    context.remove_latest_object(2)
    assert context.object_bounds(focused_only=True) is None


def test_remove_latest_object_removes_several() -> None:
    context = _context()
    context.remove_latest_object(3)
    assert context.object_bounds() is None


def test_remove_latest_object_defaults_to_one() -> None:
    context = _context()
    context.remove_latest_object()
    assert context.object_bounds(focused_only=True) is not None


def test_remove_latest_object_rejects_too_many() -> None:
    context = _context()
    with pytest.raises(IndexError):
        context.remove_latest_object(4)
    # the map is untouched after a rejected removal
    assert context.object_bounds() is not None
