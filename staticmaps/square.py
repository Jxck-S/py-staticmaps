"""py-staticmaps - square"""

# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import math
import typing

import s2sphere  # type: ignore

from .cairo_renderer import CairoRenderer
from .color import RED, Color
from .object import Object, PixelBoundsT
from .pillow_renderer import PillowRenderer
from .svg_renderer import SvgRenderer


class Square(Object):
    """A filled square drawn at a fixed pixel size, optionally rotated.

    size is the side length in pixels and the shape is centred on its
    coordinate, so it keeps the same on-screen size at every zoom level.
    angle rotates the square clockwise about its centre, in degrees, which is
    useful for conveying a heading.

    stroke_width is only honoured by the SVG renderer, matching Marker.
    """

    def __init__(
        self,
        latlng: s2sphere.LatLng,
        color: Color = RED,
        size: int = 10,
        stroke_width: int = 1,
        angle: typing.Optional[float] = None,
    ) -> None:
        Object.__init__(self)
        self._latlng = latlng.normalized()
        self._color = color
        self._size = size
        self._stroke_width = stroke_width
        self._angle = angle

    def latlng(self) -> s2sphere.LatLng:
        """Return LatLng of the square

        Returns:
            s2sphere.LatLng: LatLng of the square
        """
        return self._latlng

    def color(self) -> Color:
        """Return color of the square

        Returns:
            Color: color object
        """
        return self._color

    def size(self) -> int:
        """Return side length of the square in pixels

        Returns:
            int: side length of the square
        """
        return self._size

    def stroke_width(self) -> int:
        """Return stroke width of the square

        Returns:
            int: stroke width of the square
        """
        return self._stroke_width

    def angle(self) -> typing.Optional[float]:
        """Return rotation of the square in degrees, or None

        Returns:
            typing.Optional[float]: rotation in degrees
        """
        return self._angle

    def bounds(self) -> s2sphere.LatLngRect:
        """Return bounds of the square

        Returns:
            s2sphere.LatLngRect: bounds of the square
        """
        return s2sphere.LatLngRect.from_point(self._latlng)

    def extra_pixel_bounds(self) -> PixelBoundsT:
        """Return extra pixel bounds of the square

        The square is centred on its coordinate. A rotated square needs its
        half-diagonal rather than its half-side, so the worst case is used.

        Returns:
            PixelBoundsT: extra pixel bounds of the square
        """
        half = 0.5 * self.size()
        if self._angle:
            half *= math.sqrt(2)
        extent = int(half + 0.5 * self.stroke_width())
        return (extent, extent, extent, extent)

    def _corners(self, x: float, y: float) -> typing.List[typing.Tuple[float, float]]:
        """Return the four corners of the square, centred on (x, y) and rotated by angle

        Parameters:
            x (float): centre x in pixels
            y (float): centre y in pixels

        Returns:
            typing.List[typing.Tuple[float, float]]: corner coordinates
        """
        angle_rad = math.radians(self._angle) if self._angle else 0.0
        half = self.size() / 2
        offsets = [(-half, -half), (half, -half), (half, half), (-half, half)]
        cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
        return [
            (offset_x * cos_a - offset_y * sin_a + x, offset_x * sin_a + offset_y * cos_a + y)
            for offset_x, offset_y in offsets
        ]

    def render_pillow(self, renderer: PillowRenderer) -> None:
        """Render square using PILLOW

        Parameters:
            renderer (PillowRenderer): pillow renderer
        """
        x, y = renderer.transformer().ll2pixel(self._latlng)
        x += renderer.offset_x()

        corners = [(int(cx), int(cy)) for cx, cy in self._corners(x, y)]
        renderer.draw().polygon(corners, fill=self.color().int_rgba())

    def render_svg(self, renderer: SvgRenderer) -> None:
        """Render square using svgwrite

        Parameters:
            renderer (SvgRenderer): svg renderer
        """
        x, y = renderer.transformer().ll2pixel(self._latlng)
        half = self.size() / 2

        extra = {"transform": f"rotate({self._angle} {x} {y})"} if self._angle else {}
        path = renderer.drawing().path(
            fill=self.color().hex_rgb(),
            stroke=self.color().text_color().hex_rgb(),
            stroke_width=self.stroke_width(),
            opacity=self.color().float_a(),
            **extra,
        )

        path.push(f"M {x - half} {y - half}")
        path.push(f"l {self.size()} 0")
        path.push(f"l 0 {self.size()}")
        path.push(f"l {-self.size()} 0")
        path.push("Z")

        renderer.group().add(path)

    def render_cairo(self, renderer: CairoRenderer) -> None:
        """Render square using cairo

        Parameters:
            renderer (CairoRenderer): cairo renderer
        """
        x, y = renderer.transformer().ll2pixel(self._latlng)

        corners = self._corners(x, y)
        renderer.context().move_to(*corners[0])
        for corner in corners[1:]:
            renderer.context().line_to(*corner)
        renderer.context().close_path()

        renderer.context().set_source_rgba(*self.color().float_rgba())
        renderer.context().fill()
