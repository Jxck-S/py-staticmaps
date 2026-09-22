"""py-staticmaps - Context"""

# pylint: disable=too-many-lines

# py-staticmaps
# Copyright (c) 2022 Florian Pigorsch; see /LICENSE for licensing information

import math
import os
import typing

import appdirs  # type: ignore
import s2sphere  # type: ignore
import svgwrite  # type: ignore
from PIL import Image as PIL_Image  # type: ignore

from .basemap import select_backend
from .cairo_renderer import CairoRenderer, cairo_is_supported
from .color import Color
from .meta import LIB_NAME
from .object import Object, PixelBoundsT
from .pillow_renderer import PillowRenderer
from .svg_renderer import SvgRenderer
from .tile_downloader import TileDownloader
from .tile_provider import TileProvider, tile_provider_OSM
from .transformer import Transformer
from .vector_tile_provider import VectorTileProvider


class Context:
    """Context"""

    # pylint: disable=too-many-instance-attributes
    def __init__(self) -> None:
        self._background_color: typing.Optional[Color] = None
        self._objects: typing.List[Object] = []
        self._focused_objects: typing.List[Object] = []
        self._focused_only: bool = False
        self._center: typing.Optional[s2sphere.LatLng] = None
        self._zoom: typing.Optional[float] = None
        self._tile_provider = tile_provider_OSM
        self._tile_downloader = TileDownloader()
        self._cache_dir = os.path.join(appdirs.user_cache_dir(LIB_NAME), "tiles")
        self._tighten_to_bounds: bool = False
        self._basemap_backend: str = "auto"
        self._pixel_ratio: float = 1.0
        self.max_zoom: typing.Optional[int] = None
        self.min_zoom: typing.Optional[int] = None

    def set_max_min_zoom(self, max_zoom: int, min_zoom: int) -> None:
        """Bound the automatically determined zoom for static map

        This only constrains the zoom computed from the object bounds; a zoom
        set explicitly with set_zoom is used as given. It is separate from the
        tile provider's own limits, which are always applied as well.

        It matters when the zoom is dynamic, such as rendering a sequence of
        images with focused-only fitting, where an unconstrained zoom changes
        from image to image as the focused bounds move. Note that when a bound
        binds, the objects are no longer guaranteed to fit the image.

        Parameters:
            max_zoom (int): highest zoom the map may be fitted to
            min_zoom (int): lowest zoom the map may be fitted to

        Raises:
            ValueError: raises value error for invalid zoom factors
        """
        if max_zoom < 0 or max_zoom > 30:
            raise ValueError(f"Bad max zoom value: {max_zoom}")
        if min_zoom < 0 or min_zoom > 30:
            raise ValueError(f"Bad min zoom value: {min_zoom}")
        self.max_zoom = max_zoom
        self.min_zoom = min_zoom

    def zoom_in_range(self, zoom: float) -> float:
        """Clamp a zoom level to the user defined range, not the tile provider's

        Parameters:
            zoom (float): zoom level

        Returns:
            float: zoom level in bounds
        """
        if self.max_zoom and zoom > self.max_zoom:
            return self.max_zoom
        if self.min_zoom and zoom < self.min_zoom:
            return self.min_zoom
        return zoom

    def load_tiles_to_mem(self) -> None:
        """Load cached tiles into memory for the zoom levels this map may use

        With set_max_min_zoom set, every level in that range is loaded;
        otherwise the single level set with set_zoom is loaded.

        Raises:
            ValueError: if neither set_zoom nor set_max_min_zoom has been called,
                so there is no zoom level to load
        """
        if self.max_zoom is None and self.min_zoom is None:
            if self._zoom is None:
                raise ValueError("no zoom to load: call set_zoom or set_max_min_zoom first")
            self._tile_downloader.load_tiles_to_mem(self._tile_provider, int(self._zoom), self._cache_dir)
        elif self.max_zoom and self.min_zoom:
            for zoom in range(self.min_zoom, self.max_zoom + 1):
                self._tile_downloader.load_tiles_to_mem(self._tile_provider, zoom, self._cache_dir)

    def reset_center_zoom(self) -> None:
        """Forget the center and zoom so the next render re-fits to the objects"""
        self._center = None
        self._zoom = None

    def set_zoom(self, zoom: float) -> None:
        """Set zoom for static map

        Vector tile providers accept a fractional zoom; raster providers are
        served from discrete tile levels, so a fractional value there only
        rescales the same tiles.

        Parameters:
            zoom (float): zoom for static map

        Raises:
            ValueError: raises value error for invalid zoom factors
        """
        if zoom < 0 or zoom > 30:
            raise ValueError(f"Bad zoom value: {zoom}")
        self._zoom = zoom

    def set_center(self, latlng: s2sphere.LatLng) -> None:
        """Set center for static map

        Parameters:
            latlng (s2sphere.LatLng): zoom for static map
        """
        self._center = latlng

    def set_background_color(self, color: Color) -> None:
        """Set background color for static map

        Parameters:
            color (s2sphere.LatLng): background color for static map
        """
        self._background_color = color

    def set_cache_dir(self, directory: str) -> None:
        """Set cache dir

        Parameters:
            directory (str): cache directory
        """
        self._cache_dir = directory

    def set_tile_downloader(self, downloader: TileDownloader) -> None:
        """Set tile downloader

        Parameters:
            downloader (TileDownloader): tile downloader
        """
        self._tile_downloader = downloader

    def set_tile_provider(self, provider: TileProvider, api_key: typing.Optional[str] = None) -> None:
        """Set tile provider

        Parameters:
            provider (TileProvider): tile provider
            api_key (str): api key (if needed)
        """
        self._tile_provider = provider
        if api_key:
            self._tile_provider.set_api_key(api_key)

    def set_tighten_to_bounds(self, tighten: bool = False) -> None:
        """Set tighten to bounds

        Parameters:
            tighten (bool): tighten or not
        """
        self._tighten_to_bounds = tighten

    def add_object(self, obj: Object, focused: bool = False) -> None:
        """Add object for the static map (e.g. line, area, marker)

        Parameters:
            obj (Object): map object
            focused (bool): also mark the object as focused. When focused-only
                mode is enabled with set_focused_only, center and zoom are
                determined from the focused objects alone, while every object
                is still rendered.
        """
        self._objects.append(obj)
        if focused:
            self._focused_objects.append(obj)

    def set_focused_only(self, focused_only: bool) -> None:
        """Determine center and zoom from the focused objects only

        Parameters:
            focused_only (bool): use only focused objects to fit the map
        """
        self._focused_only = focused_only

    def focused_only(self) -> bool:
        """Return whether center and zoom are determined from focused objects only

        Returns:
            bool: focused-only mode
        """
        return self._focused_only

    def reset_focused_objects(self) -> None:
        """Forget every object previously marked as focused

        The objects themselves remain on the map; only their focused status
        is cleared.
        """
        self._focused_objects = []

    def remove_latest_object(self, count: int = 1) -> None:
        """Remove the most recently added objects from the static map

        Parameters:
            count (int): how many objects to remove, defaults to 1

        Raises:
            IndexError: if there are fewer than count objects on the map
        """
        if count > len(self._objects):
            raise IndexError(f"cannot remove {count} objects, the map has {len(self._objects)}")
        for _ in range(count):
            obj = self._objects.pop()
            if obj in self._focused_objects:
                self._focused_objects.remove(obj)

    def set_basemap_backend(self, name: str) -> None:
        """Set the backend used to render vector tile providers

        Parameters:
            name (str): "auto" or "pymgl"
        """
        self._basemap_backend = name

    def set_pixel_ratio(self, ratio: float) -> None:
        """Set the pixel ratio for vector tile providers

        A ratio of 2 renders the same geographic area at twice the pixel
        density, the way a HiDPI display or a print job wants it. This is
        distinct from asking for a larger image, which instead shows more of
        the world at the same density.

        Object *positions* scale automatically, but object *sizes* -- marker
        size, line width -- are given in pixels and do not, so scale them by
        the same ratio to keep their proportions.

        Only vector providers honour this; raster tiles are served at a fixed
        density.

        Parameters:
            ratio (float): pixel ratio, e.g. 2.0 for a HiDPI render

        Raises:
            ValueError: raises value error if the ratio is not positive
        """
        if ratio <= 0:
            raise ValueError(f"Bad pixel ratio: {ratio}")
        self._pixel_ratio = ratio

    def pixel_ratio(self) -> float:
        """Return the pixel ratio, which is 1.0 for raster providers

        Returns:
            float: pixel ratio actually applied
        """
        return self._pixel_ratio if self._tile_provider.is_vector() else 1.0

    def _transformer(self, width: int, height: int, zoom: float, center: s2sphere.LatLng) -> Transformer:
        """Build a transformer covering the rendered pixel area

        At a pixel ratio of r the image is r times larger in each direction
        while covering the same area, which is exactly what one extra zoom
        level per doubling describes -- so the projection is shifted by
        log2(r) rather than the tile grid being rescaled.

        Parameters:
            width (int): width of static map in logical pixels
            height (int): height of static map in logical pixels
            zoom (float): zoom of static map
            center (s2sphere.LatLng): center of static map

        Returns:
            Transformer: transformer for the rendered image
        """
        ratio = self.pixel_ratio()
        return Transformer(
            int(width * ratio),
            int(height * ratio),
            zoom + math.log2(ratio),
            center,
            self._tile_provider.tile_size(),
        )

    def _render_base(
        self,
        renderer: typing.Any,
        width: int,
        height: int,
        zoom: float,
        center: s2sphere.LatLng,
    ) -> None:
        """Render the base map, either from raster tiles or a vector style

        A vector provider is rendered as a single image covering the whole
        map, because label placement needs the entire viewport. Note that
        tighten_to_bounds is not applied in that case.

        Parameters:
            renderer (Renderer): renderer of the static map
            width (int): width of static map
            height (int): height of static map
            zoom (float): zoom of static map
            center (s2sphere.LatLng): center of static map
        """
        if not self._tile_provider.is_vector():
            renderer.render_tiles(self._fetch_tile, self._objects, self._tighten_to_bounds)
            return

        assert isinstance(self._tile_provider, VectorTileProvider)
        backend = select_backend(self._basemap_backend)
        image_data = backend.render(
            self._tile_provider.style(),
            width,
            height,
            zoom,
            center.lng().degrees,
            center.lat().degrees,
            self.pixel_ratio(),
        )
        renderer.render_basemap(image_data)

    def render_cairo(self, width: int, height: int, attribution: bool = True) -> typing.Any:
        """Render area using cairo

        Parameters:
            width (int): width of static map
            height (int): height of static map

        Returns:
            cairo.ImageSurface: cairo image

        Raises:
            RuntimeError: raises runtime error if cairo is not available
            RuntimeError: raises runtime error if map has no center and
                zoom
        """
        if not cairo_is_supported():
            raise RuntimeError('You need to install the "cairo" module to enable "render_cairo".')

        center, zoom = self.determine_center_zoom(width, height, self._focused_only)
        if center is None or zoom is None:
            raise RuntimeError("Cannot render map without center/zoom.")

        trans = self._transformer(width, height, zoom, center)

        renderer = CairoRenderer(trans)
        renderer.render_background(self._background_color)
        self._render_base(renderer, width, height, zoom, center)
        renderer.render_objects(self._objects, self._tighten_to_bounds)
        if attribution:
            renderer.render_attribution(self._tile_provider.attribution())

        return renderer.image_surface()

    def render_pillow(self, width: int, height: int, attribution: bool = True) -> PIL_Image.Image:
        """Render context using PILLOW

        Parameters:
            width (int): width of static map
            height (int): height of static map

        Returns:
            PIL_Image: pillow image

        Raises:
            RuntimeError: raises runtime error if map has no center and zoom
        """
        center, zoom = self.determine_center_zoom(width, height, self._focused_only)
        if center is None or zoom is None:
            raise RuntimeError("Cannot render map without center/zoom.")

        trans = self._transformer(width, height, zoom, center)

        renderer = PillowRenderer(trans)
        renderer.render_background(self._background_color)
        self._render_base(renderer, width, height, zoom, center)
        renderer.render_objects(self._objects, self._tighten_to_bounds)
        if attribution:
            renderer.render_attribution(self._tile_provider.attribution())

        return renderer.image()

    def render_svg(self, width: int, height: int) -> svgwrite.Drawing:
        """Render context using svgwrite

        Parameters:
            width (int): width of static map
            height (int): height of static map

        Returns:
            svgwrite.Drawing: svg drawing

        Raises:
            RuntimeError: raises runtime error if map has no center and zoom
        """
        center, zoom = self.determine_center_zoom(width, height, self._focused_only)
        if center is None or zoom is None:
            raise RuntimeError("Cannot render map without center/zoom.")

        trans = self._transformer(width, height, zoom, center)

        renderer = SvgRenderer(trans)
        renderer.render_background(self._background_color)
        self._render_base(renderer, width, height, zoom, center)
        renderer.render_objects(self._objects, self._tighten_to_bounds)
        renderer.render_attribution(self._tile_provider.attribution())

        return renderer.drawing()

    def object_bounds(self, focused_only: bool = False) -> typing.Optional[s2sphere.LatLngRect]:
        """return maximum bounds of all objects

        Parameters:
            focused_only (bool): consider only objects added with focused=True

        Returns:
            s2sphere.LatLngRect: maximum of all object bounds
        """
        objects = self._focused_objects if focused_only else self._objects
        bounds = None
        if len(objects) != 0:
            bounds = s2sphere.LatLngRect()
            for obj in objects:
                assert bounds
                bounds = bounds.union(obj.bounds())
        return bounds

    def extra_pixel_bounds(self) -> PixelBoundsT:
        """return extra pixel bounds from all objects

        Returns:
            PixelBoundsT: extra pixel object bounds
        """
        max_l, max_t, max_r, max_b = 0, 0, 0, 0
        attribution = self._tile_provider.attribution()
        if (attribution is None) or (attribution == ""):
            max_b = max(max_b, 12)
        for obj in self._objects:
            l, t, r, b = obj.extra_pixel_bounds()
            max_l = max(max_l, l)
            max_t = max(max_t, t)
            max_r = max(max_r, r)
            max_b = max(max_b, b)
        return max_l, max_t, max_r, max_b

    def determine_center_zoom(
        self, width: int, height: int, focused_only: bool = False
    ) -> typing.Tuple[typing.Optional[s2sphere.LatLng], typing.Optional[float]]:
        """return center and zoom of static map

        Parameters:
            width (int): width of static map
            height (int): height of static map
            focused_only (bool): fit to the focused objects only

        Returns:
            tuple: center, zoom
        """
        if self._center is not None:
            if self._zoom is not None:
                return self._center, self._clamp_zoom(self._zoom)
            b = self.object_bounds(focused_only)
            return self._center, self._determine_zoom(width, height, b, self._center)

        b = self.object_bounds(focused_only)
        if b is None:
            return None, None

        c = self._determine_center(b)
        z = self._zoom
        if z is None:
            z = self._determine_zoom(width, height, b, c)
        if z is None:
            return None, None
        return self._adjust_center(width, height, c, z), z

    def _determine_zoom(
        self, width: int, height: int, b: typing.Optional[s2sphere.LatLngRect], c: s2sphere.LatLng
    ) -> typing.Optional[float]:
        if b is None:
            b = s2sphere.LatLngRect(c, c)
        else:
            b = b.union(s2sphere.LatLngRect(c, c))
        assert b
        if b.is_point():
            return self._clamp_zoom(self.zoom_in_range(15))

        pixel_margin = self.extra_pixel_bounds()

        w = (width - pixel_margin[0] - pixel_margin[2]) / self._tile_provider.tile_size()
        h = (height - pixel_margin[1] - pixel_margin[3]) / self._tile_provider.tile_size()
        # margins are bigger than target image size => ignore them
        if w <= 0 or h <= 0:
            w = width / self._tile_provider.tile_size()
            h = height / self._tile_provider.tile_size()

        min_y = (1.0 - math.log(math.tan(b.lat_lo().radians) + (1.0 / math.cos(b.lat_lo().radians)))) / (2 * math.pi)
        max_y = (1.0 - math.log(math.tan(b.lat_hi().radians) + (1.0 / math.cos(b.lat_hi().radians)))) / (2 * math.pi)
        dx = (b.lng_hi().degrees - b.lng_lo().degrees) / 360.0
        if dx < 0:
            dx += math.ceil(math.fabs(dx))
        if dx > 1:
            dx -= math.floor(dx)
        dy = math.fabs(max_y - min_y)

        # A vector style is rendered at an arbitrary scale rather than
        # assembled from discrete tile levels, so it can fit the bounds
        # exactly instead of stepping down to the next whole zoom.
        if self._tile_provider.is_vector():
            fitted = []
            if dx > 0:
                fitted.append(math.log2(w / dx))
            if dy > 0:
                fitted.append(math.log2(h / dy))
            if fitted:
                return self._clamp_zoom(self.zoom_in_range(min(fitted)))

        for zoom in range(1, self._tile_provider.max_zoom()):
            tiles = 2**zoom
            if (dx * tiles > w) or (dy * tiles > h):
                return self._clamp_zoom(self.zoom_in_range(zoom - 1))
        return self._clamp_zoom(self.zoom_in_range(15))

    @staticmethod
    def _determine_center(b: s2sphere.LatLngRect) -> s2sphere.LatLng:
        y1 = math.log((1 + math.sin(b.lat_lo().radians)) / (1 - math.sin(b.lat_lo().radians))) / 2
        y2 = math.log((1 + math.sin(b.lat_hi().radians)) / (1 - math.sin(b.lat_hi().radians))) / 2
        lat = math.atan(math.sinh((y1 + y2) / 2)) * 180 / math.pi
        lng = b.get_center().lng().degrees
        return s2sphere.LatLng.from_degrees(lat, lng)

    def _adjust_center(self, width: int, height: int, center: s2sphere.LatLng, zoom: float) -> s2sphere.LatLng:
        if len(self._objects) == 0:
            return center

        trans = Transformer(width, height, zoom, center, self._tile_provider.tile_size())

        min_x = None
        max_x = None
        min_y = None
        max_y = None
        for obj in self._objects:
            l, t, r, b = obj.pixel_rect(trans)
            if min_x is None:
                min_x = l
                max_x = r
                min_y = t
                max_y = b
            else:
                min_x = min(min_x, l)  # type: ignore
                max_x = max(max_x, r)  # type: ignore
                min_y = min(min_y, t)  # type: ignore
                max_y = max(max_y, b)  # type: ignore
        assert min_x is not None
        assert max_x is not None
        assert min_y is not None
        assert max_y is not None

        # margins are bigger than the image => ignore
        if (max_x - min_x) > width or (max_y - min_y) > height:
            return center

        return trans.pixel2ll((max_x + min_x) * 0.5, (max_y + min_y) * 0.5)

    def _fetch_tile(self, z: int, x: int, y: int) -> typing.Optional[bytes]:
        return self._tile_downloader.get(self._tile_provider, self._cache_dir, z, x, y)

    def _clamp_zoom(self, zoom: typing.Optional[float]) -> typing.Optional[float]:
        if zoom is None:
            return None
        if zoom < 0:
            return 0
        if zoom > self._tile_provider.max_zoom():
            return self._tile_provider.max_zoom()
        return zoom
