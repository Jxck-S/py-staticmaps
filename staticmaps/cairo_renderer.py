"""py-staticmaps CairoRenderer"""

# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import io
import math
import sys
import typing

# import s2sphere  # type: ignore

try:
    import cairo  # type: ignore
except ImportError:
    pass

from PIL import Image as PIL_Image  # type: ignore

from .color import BLACK, WHITE, Color
from .renderer import Renderer
from .transformer import Transformer

if typing.TYPE_CHECKING:
    # avoid circlic import
    from .object import Object  # pylint: disable=cyclic-import


def cairo_is_supported() -> bool:
    """Check whether cairo is supported

    Returns:
        bool: Is cairo supported
    """
    return "cairo" in sys.modules


# Dummy types, so that type annotation works if cairo is missing.
cairo_Context = typing.Any
cairo_ImageSurface = typing.Any


class CairoRenderer(Renderer):
    """An image renderer using cairo that extends a generic renderer class"""

    def __init__(self, transformer: Transformer) -> None:
        Renderer.__init__(self, transformer)

        if not cairo_is_supported():
            raise RuntimeError("Cannot render to Cairo since the 'cairo' module could not be imported.")

        self._surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, *self._trans.image_size())
        self._context = cairo.Context(self._surface)

    def image_surface(self) -> cairo_ImageSurface:
        """
        Returns:
            cairo.ImageSurface: cairo image surface
        """
        return self._surface

    def context(self) -> cairo_Context:
        """
        Returns:
            cairo.Context: cairo context
        """
        return self._context

    @staticmethod
    def create_image(image_data: bytes) -> cairo_ImageSurface:
        """Create a cairo image

        Parameters:
            image_data (bytes): Image data

        Returns:
            cairo.ImageSurface: cairo image surface
        """
        image = PIL_Image.open(io.BytesIO(image_data))
        if image.format == "PNG":
            return cairo.ImageSurface.create_from_png(io.BytesIO(image_data))
        png_bytes = io.BytesIO()
        image.save(png_bytes, format="PNG")
        png_bytes.flush()
        png_bytes.seek(0)
        return cairo.ImageSurface.create_from_png(png_bytes)

    def render_objects(
        self,
        objects: typing.List["Object"],
        tighten: bool,
    ) -> None:
        """Render all objects of static map

        Parameters:
            objects (typing.List["Object"]): objects of static map
            tighten (bool): tighten to boundaries
        """
        x_count = math.ceil(self._trans.image_width() / (2 * self._trans.world_width()))
        for obj in objects:
            for p in range(-x_count, x_count + 1):
                self._context.save()
                self._context.translate(p * self._trans.world_width(), 0)
                obj.render_cairo(self)
                self._context.restore()

    def render_background(self, color: typing.Optional[Color]) -> None:
        """Render background of static map

        Parameters:
            color (typing.Optional[Color]): background color
        """
        if color is None:
            return
        self._context.set_source_rgb(*color.float_rgb())
        self._context.rectangle(0, 0, *self._trans.image_size())
        self._context.fill()

    def render_tiles(
        self,
        download: typing.Callable[[int, int, int], typing.Optional[bytes]],
        objects: typing.List["Object"],
        tighten: bool,
    ) -> None:
        """Render tiles of static map

        Parameters:
            download (typing.Callable[[int, int, int], typing.Optional[bytes]]): url of tiles provider
            objects (typing.List["Object"]): objects of static map
            tighten (bool): tighten to boundaries
        """
        for yy in range(0, self._trans.tiles_y()):
            y = self._trans.first_tile_y() + yy
            if y < 0 or y >= self._trans.number_of_tiles():
                continue
            for xx in range(0, self._trans.tiles_x()):
                x = (self._trans.first_tile_x() + xx) % self._trans.number_of_tiles()
                try:
                    tile_img = self.fetch_tile(download, x, y)
                    if tile_img is None:
                        continue
                    self._context.save()
                    self._context.translate(
                        int(xx * self._trans.tile_size() + self._trans.tile_offset_x()),
                        int(yy * self._trans.tile_size() + self._trans.tile_offset_y()),
                    )
                    self._context.set_source_surface(tile_img)
                    self._context.paint()
                    self._context.restore()
                except RuntimeError:
                    pass

    def render_attribution(self, attribution: typing.Optional[str]) -> None:
        """Render attribution from given tiles provider

        Parameters:
            attribution (typing.Optional[str]:): Attribution for the given tiles provider
        """
        if (attribution is None) or (attribution == ""):
            return
        width, height = self._trans.image_size()
        self._context.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        font_size = 9.0
        while True:
            self._context.set_font_size(font_size)
            _, f_descent, f_height, _, _ = self._context.font_extents()
            t_width = self._context.text_extents(attribution).width
            if t_width < width - 4:
                break
            font_size -= 0.25
        self._context.set_source_rgba(*WHITE.float_rgb(), 0.8)
        self._context.rectangle(0, height - f_height - f_descent - 2, width, height)
        self._context.fill()

        self._context.set_source_rgb(*BLACK.float_rgb())
        self._context.move_to(4, height - f_descent - 2)
        self._context.show_text(attribution)
        self._context.stroke()

    def fetch_tile(
        self, download: typing.Callable[[int, int, int], typing.Optional[bytes]], x: int, y: int
    ) -> typing.Optional[cairo_ImageSurface]:
        """Fetch tiles from given tiles provider

        Parameters:
            download (typing.Callable[[int, int, int], typing.Optional[bytes]]):
                callable
            x (int): width
            y (int): height

        Returns:
            typing.Optional[cairo_ImageSurface]: cairo image surface
        """
        image_data = download(self._trans.zoom(), x, y)
        if image_data is None:
            return None
        return self.create_image(image_data)
