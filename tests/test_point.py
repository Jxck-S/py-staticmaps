"""py-staticmaps - Test Point"""

# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

from PIL import Image as PIL_Image

import staticmaps


def _count_pixels(image: PIL_Image.Image, rgb: tuple) -> int:
    """Count pixels of the given RGB colour in an image."""
    data = list(image.convert("RGB").get_flattened_data())
    return sum(1 for pixel in data if pixel == rgb)


def test_creation() -> None:
    staticmaps.Point(staticmaps.create_latlng(48, 8), color=staticmaps.YELLOW, size=8)


def test_bounds() -> None:
    point = staticmaps.Point(staticmaps.create_latlng(48, 8))
    assert point.bounds().is_point()


def test_extra_pixel_bounds_is_symmetric() -> None:
    """A Point is centred on its coordinate, unlike Marker which is a pin."""
    point = staticmaps.Point(staticmaps.create_latlng(48, 8), size=20, stroke_width=2)
    left, top, right, bottom = point.extra_pixel_bounds()
    assert left == top == right == bottom == 11


def test_latlng_is_normalized() -> None:
    point = staticmaps.Point(staticmaps.create_latlng(22.3, 190.0))
    assert -180.0 <= point.latlng().lng().degrees <= 180.0


def test_render_pillow_draws_a_disc() -> None:
    context = staticmaps.Context()
    context.set_tile_provider(staticmaps.tile_provider_None)
    context.add_object(staticmaps.Point(staticmaps.create_latlng(48, 8), color=staticmaps.RED, size=20))
    image = context.render_pillow(200, 200)
    drawn = _count_pixels(image, staticmaps.RED.int_rgba()[:3])

    # a disc of diameter 20 covers about pi * 10^2 = 314 pixels
    assert 250 < drawn < 400
