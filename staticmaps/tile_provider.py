"""py-staticmaps - tile_provider"""

# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import string
import typing
import urllib.parse


class TileProvider:
    """A tile provider class with several pre-defined tile providers"""

    # pylint: disable=too-many-instance-attributes

    def __init__(
        self,
        name: str,
        url_pattern: str,
        shards: typing.Optional[typing.List[str]] = None,
        api_key: typing.Optional[str] = None,
        attribution: typing.Optional[str] = None,
        max_zoom: int = 24,
        tile_size: int = 256,
        key_param: typing.Optional[str] = None,
        requires_key: bool = False,
    ) -> None:
        self._name = name
        self._tile_size = tile_size
        self._key_param = key_param
        self._requires_key = requires_key
        self._url_pattern = string.Template(url_pattern)
        self._shards = shards
        self._api_key = api_key
        self._attribution = attribution
        self._max_zoom = max_zoom if ((max_zoom is not None) and (max_zoom <= 20)) else 20

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TileProvider):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (
            self._name == other._name
            and str(self._url_pattern) == str(other._url_pattern)
            and self._shards == other._shards
            and self._api_key == other._api_key
            and self._attribution == other._attribution
            and self._max_zoom == other._max_zoom
            and self._tile_size == other._tile_size
            and self._key_param == other._key_param
            and self._requires_key == other._requires_key
        )

    def set_api_key(self, key: str) -> None:
        """Set an api key

        Parameters:
            key (str): api key
        """
        self._api_key = key

    def pixel_density(self) -> float:
        """Return how many pixels this provider packs per standard tile pixel

        A provider serving "@2x" tiles reports 2.0. This is the raster
        counterpart of Context.set_pixel_ratio(): raster density comes from
        the tiles a provider serves, vector density from the render call, and
        both trade geographic coverage for detail the same way.

        Returns:
            float: tile_size divided by the standard 256
        """
        return self._tile_size / 256

    def key_param(self) -> typing.Optional[str]:
        """Return the query parameter this provider expects its api key in

        Providers agree on passing the key as a query parameter and disagree
        on what to call it: "key", "api_key" and "access-token" are all in
        use. Naming it here keeps one mechanism for all of them, with the
        provider supplying the parameter name and the user supplying the key.

        Returns:
            typing.Optional[str]: parameter name, or None if the provider
            takes no key
        """
        return self._key_param

    def requires_key(self) -> bool:
        """Return whether this provider refuses to serve tiles without a key

        Returns:
            bool: True if an api key is mandatory
        """
        return self._requires_key

    def has_api_key(self) -> bool:
        """Return whether an api key has been set

        Returns:
            bool: True if a non-empty api key is set
        """
        return bool(self._api_key)

    def name(self) -> str:
        """Return the name of the tile provider

        Returns:
            str: name of tile provider
        """
        return self._name

    def attribution(self) -> typing.Optional[str]:
        """Return the attribution of the tile provider

        Returns:
            typing.Optional[str]: attribution of tile provider if
            available
        """
        return self._attribution

    def tile_size(self) -> int:
        """Return the tile size

        A provider serving "@2x" tiles returns 512: the tile covers the same
        ground as a 256px one but carries four times the pixels, which is how
        raster providers express a high density display.

        Returns:
            int: tile size
        """
        return self._tile_size

    @staticmethod
    def is_vector() -> bool:
        """Return whether this provider needs a basemap backend

        Returns:
            bool: False for raster tile providers
        """
        return False

    def max_zoom(self) -> int:
        """Return the maximum zoom of the tile provider

        Returns:
            int: maximum zoom
        """
        return self._max_zoom

    def url(self, zoom: int, x: int, y: int) -> typing.Optional[str]:
        """Return the url of the tile provider

        Parameters:
            zoom (int): zoom for static map
            x (int): x value of center for the static map
            y (int): y value of center for the static map

        Returns:
            typing.Optional[str]: url with zoom, x and y values

        Raises:
            ValueError: raises value error if the provider requires an api key
                and none has been set
        """
        if len(self._url_pattern.template) == 0:
            return None
        if (zoom < 0) or (zoom > self._max_zoom):
            return None
        if self._requires_key and not self._api_key:
            raise ValueError(
                f'tile provider "{self._name}" requires an api key; ' f"call set_api_key() before rendering"
            )
        shard = None
        if self._shards is not None and len(self._shards) > 0:
            shard = self._shards[(x + y) % len(self._shards)]
        # an unset key must not reach the url as the string "None"
        url = self._url_pattern.substitute(s=shard, z=zoom, x=x, y=y, k=self._api_key or "")
        if self._key_param and self._api_key:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}{self._key_param}={urllib.parse.quote(self._api_key, safe='')}"
        return url


# pylint: disable=invalid-name
tile_provider_OSM = TileProvider(
    "osm",
    url_pattern="https://$s.tile.openstreetmap.org/$z/$x/$y.png",
    shards=["a", "b", "c"],
    attribution="Maps & Data (C) OpenStreetMap.org contributors",
    max_zoom=19,
)

tile_provider_StamenTerrain = TileProvider(
    "stamen-terrain",
    url_pattern="http://$s.tile.stamen.com/terrain/$z/$x/$y.png",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) Stamen, Data (C) OpenStreetMap.org contributors",
    max_zoom=18,
)

tile_provider_StamenToner = TileProvider(
    "stamen-toner",
    url_pattern="http://$s.tile.stamen.com/toner/$z/$x/$y.png",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) Stamen, Data (C) OpenStreetMap.org contributors",
    max_zoom=20,
)

tile_provider_StamenTonerLite = TileProvider(
    "stamen-toner-lite",
    url_pattern="http://$s.tile.stamen.com/toner-lite/$z/$x/$y.png",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) Stamen, Data (C) OpenStreetMap.org contributors",
    max_zoom=20,
)

tile_provider_ArcGISWorldImagery = TileProvider(
    "arcgis-worldimagery",
    url_pattern="https://server.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/$z/$y/$x",
    attribution="Source: Esri, Maxar, GeoEye, Earthstar Geographics, "
    "CNES/Airbus DS, USDA, USGS, AeroGRID, IGN, and the GIS User Community",
    max_zoom=24,
)

tile_provider_Carto = TileProvider(
    "carto",
    url_pattern="https://$s.basemaps.cartocdn.com/rastertiles/light_all/$z/$x/$y.png",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) CARTO (C) OpenStreetMap.org contributors",
    max_zoom=20,
    key_param="key",
    requires_key=True,
)

tile_provider_Carto2x = TileProvider(
    "carto-2x",
    url_pattern="https://$s.basemaps.cartocdn.com/rastertiles/light_all/$z/$x/$y@2x.png",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) CARTO (C) OpenStreetMap.org contributors",
    max_zoom=20,
    tile_size=512,
    key_param="key",
    requires_key=True,
)

tile_provider_CartoNoLabels = TileProvider(
    "carto-nolabels",
    url_pattern="https://$s.basemaps.cartocdn.com/rastertiles/light_nolabels/$z/$x/$y.png",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) CARTO (C) OpenStreetMap.org contributors",
    max_zoom=20,
    key_param="key",
    requires_key=True,
)

tile_provider_CartoNoLabels2x = TileProvider(
    "carto-nolabels-2x",
    url_pattern="https://$s.basemaps.cartocdn.com/rastertiles/light_nolabels/$z/$x/$y@2x.png",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) CARTO (C) OpenStreetMap.org contributors",
    max_zoom=20,
    tile_size=512,
    key_param="key",
    requires_key=True,
)

tile_provider_CartoDark = TileProvider(
    "carto-dark",
    url_pattern="https://$s.basemaps.cartocdn.com/rastertiles/dark_all/$z/$x/$y.png",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) CARTO (C) OpenStreetMap.org contributors",
    max_zoom=20,
    key_param="key",
    requires_key=True,
)

tile_provider_CartoDark2x = TileProvider(
    "carto-dark-2x",
    url_pattern="https://$s.basemaps.cartocdn.com/rastertiles/dark_all/$z/$x/$y@2x.png",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) CARTO (C) OpenStreetMap.org contributors",
    max_zoom=20,
    tile_size=512,
    key_param="key",
    requires_key=True,
)

tile_provider_CartoDarkNoLabels = TileProvider(
    "carto-darknolabels",
    url_pattern="https://$s.basemaps.cartocdn.com/rastertiles/dark_nolabels/$z/$x/$y.png",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) CARTO (C) OpenStreetMap.org contributors",
    max_zoom=20,
    key_param="key",
    requires_key=True,
)

tile_provider_CartoDarkNoLabels2x = TileProvider(
    "carto-darknolabels-2x",
    url_pattern="https://$s.basemaps.cartocdn.com/rastertiles/dark_nolabels/$z/$x/$y@2x.png",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) CARTO (C) OpenStreetMap.org contributors",
    max_zoom=20,
    tile_size=512,
    key_param="key",
    requires_key=True,
)

tile_provider_CartoVoyager = TileProvider(
    "carto-voyager",
    url_pattern="https://$s.basemaps.cartocdn.com/rastertiles/voyager/$z/$x/$y.png",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) CARTO (C) OpenStreetMap.org contributors",
    max_zoom=20,
    key_param="key",
    requires_key=True,
)

tile_provider_CartoVoyager2x = TileProvider(
    "carto-voyager-2x",
    url_pattern="https://$s.basemaps.cartocdn.com/rastertiles/voyager/$z/$x/$y@2x.png",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) CARTO (C) OpenStreetMap.org contributors",
    max_zoom=20,
    tile_size=512,
    key_param="key",
    requires_key=True,
)

tile_provider_CartoVoyagerNoLabels = TileProvider(
    "carto-voyagernolabels",
    url_pattern="https://$s.basemaps.cartocdn.com/rastertiles/voyager_nolabels/$z/$x/$y.png",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) CARTO (C) OpenStreetMap.org contributors",
    max_zoom=20,
    key_param="key",
    requires_key=True,
)

tile_provider_CartoVoyagerNoLabels2x = TileProvider(
    "carto-voyagernolabels-2x",
    url_pattern="https://$s.basemaps.cartocdn.com/rastertiles/voyager_nolabels/$z/$x/$y@2x.png",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) CARTO (C) OpenStreetMap.org contributors",
    max_zoom=20,
    tile_size=512,
    key_param="key",
    requires_key=True,
)

tile_provider_StadiaAlidadeSmooth = TileProvider(
    "stadia-alidade-smooth",
    url_pattern="https://tiles.stadiamaps.com/tiles/alidade_smooth/$z/$x/$y.png",
    attribution="Maps (C) Stadia Maps (C) OpenMapTiles (C) OpenStreetMap.org contributors",
    max_zoom=20,
    key_param="api_key",
    requires_key=True,
)

tile_provider_StadiaAlidadeSmoothDark = TileProvider(
    "stadia-alidade-smooth-dark",
    url_pattern="https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/$z/$x/$y.png",
    attribution="Maps (C) Stadia Maps (C) OpenMapTiles (C) OpenStreetMap.org contributors",
    max_zoom=20,
    key_param="api_key",
    requires_key=True,
)

tile_provider_JawgLight = TileProvider(
    "jawg-light",
    url_pattern="https://$s.tile.jawg.io/jawg-light/$z/$x/$y.png",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) Jawg Maps (C) OpenStreetMap.org contributors",
    max_zoom=22,
    key_param="access-token",
    requires_key=True,
)

tile_provider_JawgDark = TileProvider(
    "jawg-dark",
    url_pattern="https://$s.tile.jawg.io/jawg-dark/$z/$x/$y.png",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) Jawg Maps (C) OpenStreetMap.org contributors",
    max_zoom=22,
    key_param="access-token",
    requires_key=True,
)

tile_provider_None = TileProvider(
    "none",
    url_pattern="",
    attribution=None,
    max_zoom=99,
)

default_tile_providers = {
    p.name(): p
    for p in (
        tile_provider_ArcGISWorldImagery,
        tile_provider_Carto,
        tile_provider_Carto2x,
        tile_provider_CartoNoLabels,
        tile_provider_CartoNoLabels2x,
        tile_provider_CartoDark,
        tile_provider_CartoDark2x,
        tile_provider_CartoDarkNoLabels,
        tile_provider_CartoDarkNoLabels2x,
        tile_provider_CartoVoyager,
        tile_provider_CartoVoyager2x,
        tile_provider_CartoVoyagerNoLabels,
        tile_provider_CartoVoyagerNoLabels2x,
        tile_provider_OSM,
        tile_provider_StadiaAlidadeSmooth,
        tile_provider_StadiaAlidadeSmoothDark,
        tile_provider_JawgLight,
        tile_provider_JawgDark,
        tile_provider_None,
    )
}
