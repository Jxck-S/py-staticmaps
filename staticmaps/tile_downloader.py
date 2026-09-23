"""py-staticmaps - tile_downloader"""

# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import logging
import os
import pathlib
import typing
import urllib.parse

import requests  # type: ignore
import slugify  # type: ignore

from .meta import GITHUB_URL, LIB_NAME, VERSION
from .tile_provider import TileProvider

REQUEST_TIMEOUT = 10


def redact_url(url: str) -> str:
    """Strip the query string from a url so it is safe to put in a message

    A provider's api key travels in the query string, so an unredacted url in
    an exception or a log leaks the key to wherever that text ends up.

    Parameters:
        url (str): url, possibly carrying an api key

    Returns:
        str: url without its query string
    """
    parts = urllib.parse.urlsplit(url)
    if not parts.query:
        return url
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, "", "")) + "?<redacted>"


class TileDownloader:
    """A tile downloader class"""

    def __init__(self) -> None:
        self._user_agent = f"Mozilla/5.0+(compatible; {LIB_NAME}/{VERSION}; {GITHUB_URL})"
        self._sanitized_name_cache: typing.Dict[str, str] = {}
        self.loaded_tiles: typing.Dict[str, typing.Dict[int, typing.Dict[int, typing.Dict[int, bytes]]]] = {}

    def load_tiles_to_mem(self, tile_provider: TileProvider, zoom: int, cache_dir: str) -> None:
        """Load every cached tile for one zoom level into memory

        Subsequent get() calls for those tiles are served from memory instead
        of re-reading them from disk, which matters when rendering many images
        over the same area.

        The whole zoom level is read, so memory use grows with the size of the
        cached area. Bound it with Context.set_max_min_zoom, or by keeping the
        tile cache directory to the area of interest.

        Parameters:
            tile_provider (TileProvider): tile provider
            zoom (int): zoom level to load
            cache_dir (str): cache directory for tiles
        """
        provider_name = tile_provider.name()
        zoom_dir = os.path.join(cache_dir, provider_name, str(zoom))
        loaded = 0
        for x_dir in os.listdir(zoom_dir):
            full_x_path = os.path.join(zoom_dir, x_dir)
            for y_img in os.listdir(full_x_path):
                x = int(x_dir)
                y = int(os.path.basename(y_img).split(".")[0])
                with open(os.path.join(full_x_path, y_img), "rb") as image:
                    self.loaded_tiles.setdefault(provider_name, {}).setdefault(zoom, {}).setdefault(x, {})[
                        y
                    ] = image.read()
                loaded += 1
        logging.info("Loaded %d tiles from storage into memory, %s at zoom %d", loaded, provider_name, zoom)

    def set_user_agent(self, user_agent: str) -> None:
        """Set the user agent for the downloader

        Parameters:
            user_agent (str): user agent
        """
        self._user_agent = user_agent

    def get(self, provider: TileProvider, cache_dir: str, zoom: int, x: int, y: int) -> typing.Optional[bytes]:
        """Get tiles

        Parameters:
            provider (TileProvider): tile provider
            cache_dir (str): cache directory for tiles
            zoom (int): zoom for static map
            x (int): x value of center for the static map
            y (int): y value of center for the static map

        Returns:
            typing.Optional[bytes]: tiles

        Raises:
            RuntimeError: raises a runtime error if the server response status is not 200
        """
        provider_name = provider.name()
        cached = self.loaded_tiles.get(provider_name, {}).get(zoom, {}).get(x, {}).get(y)
        if cached is not None:
            return cached

        file_name = None
        if cache_dir is not None:
            file_name = self.cache_file_name(provider, cache_dir, zoom, x, y)
            if os.path.isfile(file_name):
                with open(file_name, "rb") as f:
                    return f.read()

        url = provider.url(zoom, x, y)
        if url is None:
            return None
        res = requests.get(url, headers={"user-agent": self._user_agent}, timeout=REQUEST_TIMEOUT)
        if res.status_code == 200:
            data = res.content
        else:
            raise RuntimeError(f"fetch {redact_url(url)} yields {res.status_code}")

        if file_name is not None:
            pathlib.Path(os.path.dirname(file_name)).mkdir(parents=True, exist_ok=True)
            with open(file_name, "wb") as f:
                f.write(data)
        return data

    def sanitized_name(self, name: str) -> str:
        """Return sanitized name

        Parameters:
            name (str): name to sanitize

        Returns:
            str: sanitized name
        """
        if name in self._sanitized_name_cache:
            return self._sanitized_name_cache[name]
        sanitized = slugify.slugify(name)
        if sanitized is None:
            sanitized = "_"
        self._sanitized_name_cache[name] = sanitized
        return sanitized

    def cache_file_name(self, provider: TileProvider, cache_dir: str, zoom: int, x: int, y: int) -> str:
        """Return a cache file name

        Parameters:
            provider (TileProvider): tile provider
            cache_dir (str): cache directory for tiles
            zoom (int): zoom for static map
            x (int): x value of center for the static map
            y (int): y value of center for the static map

        Returns:
            str: cache file name
        """
        return os.path.join(cache_dir, self.sanitized_name(provider.name()), str(zoom), str(x), f"{y}.png")
