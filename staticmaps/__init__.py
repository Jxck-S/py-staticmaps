"""py-staticmaps __init__"""

# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

# flake8: noqa
from .area import Area
from .basemap import BasemapBackend, PyMGLBackend, select_backend
from .bounds import Bounds
from .cairo_renderer import CairoRenderer, cairo_is_supported
from .circle import Circle
from .color import (
    BLACK,
    BLUE,
    BROWN,
    GREEN,
    ORANGE,
    PURPLE,
    RED,
    TRANSPARENT,
    WHITE,
    YELLOW,
    Color,
    parse_color,
    random_color,
)
from .context import Context
from .coordinates import create_latlng, parse_latlng, parse_latlngs, parse_latlngs2rect
from .image_marker import ImageMarker
from .line import Line
from .marker import Marker
from .meta import GITHUB_URL, LIB_NAME, VERSION
from .object import Object, PixelBoundsT
from .pillow_renderer import PillowRenderer
from .point import Point
from .square import Square
from .svg_renderer import SvgRenderer
from .tile_downloader import TileDownloader
from .tile_provider import (
    TileProvider,
    default_tile_providers,
    tile_provider_ArcGISWorldImagery,
    tile_provider_Carto,
    tile_provider_Carto2x,
    tile_provider_CartoDark,
    tile_provider_CartoDark2x,
    tile_provider_CartoDarkNoLabels,
    tile_provider_CartoDarkNoLabels2x,
    tile_provider_CartoNoLabels,
    tile_provider_CartoNoLabels2x,
    tile_provider_CartoVoyager,
    tile_provider_CartoVoyager2x,
    tile_provider_CartoVoyagerNoLabels,
    tile_provider_CartoVoyagerNoLabels2x,
    tile_provider_JawgDark,
    tile_provider_JawgLight,
    tile_provider_None,
    tile_provider_OSM,
    tile_provider_StadiaAlidadeSmooth,
    tile_provider_StadiaAlidadeSmoothDark,
    tile_provider_StamenTerrain,
    tile_provider_StamenToner,
    tile_provider_StamenTonerLite,
)
from .transformer import Transformer
from .vector_tile_provider import (
    VectorTileProvider,
    default_vector_tile_providers,
    maptoolkit,
    openfreemap,
    tile_provider_MaptoolkitDark,
    tile_provider_MaptoolkitLight,
    tile_provider_MaptoolkitStreet,
    tile_provider_OpenFreeMapBright,
    tile_provider_OpenFreeMapDark,
    tile_provider_OpenFreeMapFiord,
    tile_provider_OpenFreeMapLiberty,
    tile_provider_OpenFreeMapPositron,
    tile_provider_VersaTilesColorful,
    tile_provider_VersaTilesEclipse,
    tile_provider_VersaTilesGraybeard,
    tile_provider_VersaTilesNeutrino,
    tile_provider_VersaTilesShadow,
    versatiles,
)

__all__ = [
    "Area",
    "Bounds",
    "CairoRenderer",
    "cairo_is_supported",
    "Circle",
    "BLACK",
    "BLUE",
    "BROWN",
    "GREEN",
    "ORANGE",
    "PURPLE",
    "RED",
    "TRANSPARENT",
    "WHITE",
    "YELLOW",
    "Color",
    "parse_color",
    "random_color",
    "Context",
    "create_latlng",
    "parse_latlng",
    "parse_latlngs",
    "parse_latlngs2rect",
    "ImageMarker",
    "Line",
    "Marker",
    "GITHUB_URL",
    "LIB_NAME",
    "VERSION",
    "Object",
    "Point",
    "PixelBoundsT",
    "PillowRenderer",
    "SvgRenderer",
    "TileDownloader",
    "TileProvider",
    "default_tile_providers",
    "tile_provider_ArcGISWorldImagery",
    "tile_provider_Carto",
    "tile_provider_Carto2x",
    "tile_provider_CartoDark",
    "tile_provider_CartoDark2x",
    "tile_provider_CartoDarkNoLabels",
    "tile_provider_CartoDarkNoLabels2x",
    "tile_provider_CartoNoLabels",
    "tile_provider_CartoNoLabels2x",
    "tile_provider_CartoVoyager",
    "tile_provider_CartoVoyager2x",
    "tile_provider_CartoVoyagerNoLabels",
    "tile_provider_CartoVoyagerNoLabels2x",
    "tile_provider_JawgDark",
    "tile_provider_JawgLight",
    "tile_provider_None",
    "tile_provider_OSM",
    "tile_provider_StadiaAlidadeSmooth",
    "tile_provider_StadiaAlidadeSmoothDark",
    "tile_provider_StamenTerrain",
    "tile_provider_StamenToner",
    "tile_provider_StamenTonerLite",
    "Square",
    "Transformer",
    "BasemapBackend",
    "PyMGLBackend",
    "select_backend",
    "VectorTileProvider",
    "default_vector_tile_providers",
    "openfreemap",
    "maptoolkit",
    "versatiles",
]
