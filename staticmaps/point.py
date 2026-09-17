"""py-staticmaps - point"""

# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import math

import s2sphere  # type: ignore

from .cairo_renderer import CairoRenderer
from .color import RED, Color
from .object import Object, PixelBoundsT
from .pillow_renderer import PillowRenderer
from .svg_renderer import SvgRenderer


class Point(Object):
    """A filled circle drawn at a fixed pixel size.

    Unlike Circle, whose radius is given in kilometres and therefore grows and
    shrinks with the zoom level, a Point keeps the same on-screen size at every
    zoom. size is the diameter in pixels and the shape is centred on its
    coordinate.

    stroke_width is only honoured by the SVG renderer, matching Marker.
    """

    def __init__(self, latlng: s2sphere.LatLng, color: Color = RED, size: int = 10, stroke_width: int = 1) -> None:
        Object.__init__(self)
        self._latlng = latlng.normalized()
        self._color = color
        self._size = size
        self._stroke_width = stroke_width

    def latlng(self) -> s2sphere.LatLng:
        """Return LatLng of the point

        Returns:
            s2sphere.LatLng: LatLng of the point
        """
        return self._latlng

    def color(self) -> Color:
        """Return color of the point

        Returns:
            Color: color object
        """
        return self._color

    def size(self) -> int:
        """Return diameter of the point in pixels

        Returns:
            int: diameter of the point
        """
        return self._size

    def stroke_width(self) -> int:
        """Return stroke width of the point

        Returns:
            int: stroke width of the point
        """
        return self._stroke_width

    def bounds(self) -> s2sphere.LatLngRect:
        """Return bounds of the point

        Returns:
            s2sphere.LatLngRect: bounds of the point
        """
        return s2sphere.LatLngRect.from_point(self._latlng)

    def extra_pixel_bounds(self) -> PixelBoundsT:
        """Return extra pixel bounds of the point

        The point is centred on its coordinate, so it extends equally in all
        four directions.

        Returns:
            PixelBoundsT: extra pixel bounds of the point
        """
        extent = int(0.5 * self.size() + 0.5 * self.stroke_width())
        return (extent, extent, extent, extent)

    def render_pillow(self, renderer: PillowRenderer) -> None:
        """Render point using PILLOW

        Parameters:
            renderer (PillowRenderer): pillow renderer
        """
        x, y = renderer.transformer().ll2pixel(self._latlng)
        x += renderer.offset_x()
        r = self.size() / 2

        renderer.draw().ellipse((x - r, y - r, x + r, y + r), fill=self.color().int_rgba())

    def render_svg(self, renderer: SvgRenderer) -> None:
        """Render point using svgwrite

        Parameters:
            renderer (SvgRenderer): svg renderer
        """
        x, y = renderer.transformer().ll2pixel(self._latlng)
        r = self.size() / 2

        path = renderer.drawing().circle(
            (x, y),
            r,
            fill=self.color().hex_rgb(),
            stroke=self.color().text_color().hex_rgb(),
            stroke_width=self.stroke_width(),
            opacity=self.color().float_a(),
        )

        renderer.group().add(path)

    def render_cairo(self, renderer: CairoRenderer) -> None:
        """Render point using cairo

        Parameters:
            renderer (CairoRenderer): cairo renderer
        """
        x, y = renderer.transformer().ll2pixel(self._latlng)
        r = self.size() / 2

        renderer.context().set_source_rgba(*self.color().float_rgba())
        renderer.context().arc(x, y, r, 0, 2 * math.pi)
        renderer.context().fill()
