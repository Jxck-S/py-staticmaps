"""py-staticmaps - Test Square"""

# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import io
import typing

from PIL import Image as PIL_Image

import staticmaps


def _count_pixels(image: PIL_Image.Image, rgb: tuple) -> int:
    """Count pixels of the given RGB colour in an image."""
    data = list(image.convert("RGB").get_flattened_data())
    return sum(1 for pixel in data if pixel == rgb)


def test_creation() -> None:
    staticmaps.Square(staticmaps.create_latlng(48, 8), color=staticmaps.YELLOW, size=8, angle=30)


def test_bounds() -> None:
    square = staticmaps.Square(staticmaps.create_latlng(48, 8))
    assert square.bounds().is_point()


def test_extra_pixel_bounds_grows_when_rotated() -> None:
    """A rotated square needs its half-diagonal, not its half-side."""
    upright = staticmaps.Square(staticmaps.create_latlng(48, 8), size=20, stroke_width=2)
    rotated = staticmaps.Square(staticmaps.create_latlng(48, 8), size=20, stroke_width=2, angle=45)
    assert upright.extra_pixel_bounds() == (11, 11, 11, 11)
    assert rotated.extra_pixel_bounds()[0] > upright.extra_pixel_bounds()[0]


def test_render_pillow_area_matches_size() -> None:
    context = staticmaps.Context()
    context.set_tile_provider(staticmaps.tile_provider_None)
    context.add_object(staticmaps.Square(staticmaps.create_latlng(48, 8), color=staticmaps.RED, size=40))
    image = context.render_pillow(200, 200)
    drawn = _count_pixels(image, staticmaps.RED.int_rgba()[:3])

    # a 40x40 square covers about 1600 pixels
    assert 1500 < drawn < 1800


def test_rotation_preserves_area_and_changes_image() -> None:
    def render(angle: typing.Optional[float]) -> typing.Tuple[int, list]:
        context = staticmaps.Context()
        context.set_tile_provider(staticmaps.tile_provider_None)
        context.add_object(
            staticmaps.Square(staticmaps.create_latlng(48, 8), color=staticmaps.RED, size=40, angle=angle)
        )
        image = context.render_pillow(200, 200)
        drawn = _count_pixels(image, staticmaps.RED.int_rgba()[:3])
        return drawn, list(image.convert("RGB").get_flattened_data())

    upright_area, upright_data = render(None)
    rotated_area, rotated_data = render(45)

    assert abs(upright_area - rotated_area) < 60
    assert upright_data != rotated_data


def test_render_svg_is_centred_and_full_size() -> None:
    """The square must be centred on its coordinate with sides of `size`."""
    context = staticmaps.Context()
    context.set_tile_provider(staticmaps.tile_provider_None)
    context.add_object(staticmaps.Square(staticmaps.create_latlng(48, 8), size=40))
    buffer = io.StringIO()
    context.render_svg(300, 300).write(buffer)
    svg = buffer.getvalue()

    # centre is (150, 150), so the path starts at (130, 130) with sides of 40
    assert "M 130.0 130.0 l 40 0 l 0 40 l -40 0 Z" in svg


def test_render_svg_applies_rotation_about_the_centre() -> None:
    context = staticmaps.Context()
    context.set_tile_provider(staticmaps.tile_provider_None)
    context.add_object(staticmaps.Square(staticmaps.create_latlng(48, 8), size=40, angle=45))
    buffer = io.StringIO()
    context.render_svg(300, 300).write(buffer)

    assert 'transform="rotate(45 150.0 150.0)"' in buffer.getvalue()
