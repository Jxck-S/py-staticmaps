"""py-staticmaps - vector_tile_provider"""

# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import hashlib
import html
import json
import re
import typing

import requests  # type: ignore

from .meta import GITHUB_URL, LIB_NAME, VERSION
from .tile_provider import TileProvider

REQUEST_TIMEOUT = 10

_RE_TAG = re.compile(r"<[^>]+>")
_RE_SPACE = re.compile(r"\s+")


def _strip_html(text: str) -> str:
    """Reduce an HTML attribution string to plain text

    Parameters:
        text (str): attribution, possibly containing markup

    Returns:
        str: plain text attribution
    """
    return _RE_SPACE.sub(" ", html.unescape(_RE_TAG.sub("", text))).strip()


class VectorTileProvider(TileProvider):
    """A vector tile provider, rendered from a MapLibre GL style.

    Unlike a raster TileProvider this does not serve pre-rendered images.
    The style is rendered to a single basemap image by a BasemapBackend, so
    url() deliberately returns None: the raster tile path is never used.
    """

    def __init__(
        self,
        name: str,
        style_url: typing.Optional[str] = None,
        style: typing.Optional[typing.Union[str, dict]] = None,
        attribution: typing.Optional[str] = None,
        max_zoom: int = 20,
        tile_size: int = 256,
    ) -> None:
        if style_url is None and style is None:
            raise ValueError("a vector tile provider needs either style_url or style")
        super().__init__(name, url_pattern="", attribution=attribution, max_zoom=max_zoom)
        self._style_url = style_url
        self._tile_size = tile_size
        self._user_agent = f"Mozilla/5.0+(compatible; {LIB_NAME}/{VERSION}; {GITHUB_URL})"
        self._style_json: typing.Optional[str] = None
        self._version_hash: typing.Optional[str] = None
        if style is not None:
            self._set_style(style if isinstance(style, str) else json.dumps(style))

    def _set_style(self, style_json: str) -> None:
        """Store a resolved style and derive attribution and cache key from it

        Parameters:
            style_json (str): MapLibre GL style as a json-encoded string
        """
        self._style_json = style_json
        parsed = json.loads(style_json)
        self._version_hash = self._resolve_version(parsed)
        if self._attribution is None:
            self._attribution = self._resolve_attribution(parsed)

    def _get(self, url: str) -> typing.Any:
        """Fetch and decode a JSON document

        Parameters:
            url (str): url to fetch

        Returns:
            typing.Any: decoded JSON

        Raises:
            RuntimeError: raises a runtime error if the server response status is not 200
        """
        res = requests.get(url, headers={"user-agent": self._user_agent}, timeout=REQUEST_TIMEOUT)
        if res.status_code != 200:
            raise RuntimeError(f"fetch {url} yields {res.status_code}")
        return res.json()

    def _source_tilejson(self, parsed: dict) -> typing.List[dict]:
        """Fetch the TileJSON of every source that references one

        Parameters:
            parsed (dict): decoded style

        Returns:
            typing.List[dict]: decoded TileJSON documents
        """
        documents = []
        for source in (parsed.get("sources") or {}).values():
            url = source.get("url")
            if not url or not url.startswith("http"):
                continue
            try:
                documents.append(self._get(url))
            except (RuntimeError, ValueError, requests.RequestException):
                continue
        return documents

    def _resolve_version(self, parsed: dict) -> str:
        """Derive a short cache key from the resolved tile urls

        OpenFreeMap embeds a dated path segment in its tile template, which
        rotates weekly. Folding it into the cache key means a data rotation or
        a style change does not serve stale imagery.

        Parameters:
            parsed (dict): decoded style

        Returns:
            str: short hex digest
        """
        seeds: typing.List[str] = []
        for document in self._source_tilejson(parsed):
            seeds.extend(document.get("tiles") or [])
        if not seeds:
            seeds = [self._style_url or ""]
        return hashlib.sha256("|".join(sorted(seeds)).encode()).hexdigest()[:8]

    def _resolve_attribution(self, parsed: dict) -> typing.Optional[str]:
        """Derive a plain text attribution from the style's sources

        Parameters:
            parsed (dict): decoded style

        Returns:
            typing.Optional[str]: attribution if one is advertised
        """
        parts: typing.List[str] = []
        for document in self._source_tilejson(parsed):
            text = _strip_html(document.get("attribution") or "")
            if text and text not in parts:
                parts.append(text)
        return " ".join(parts) if parts else None

    def style(self) -> str:
        """Return the MapLibre GL style, fetching it on first use

        Returns:
            str: style as a json-encoded string

        Raises:
            RuntimeError: raises a runtime error if the style cannot be fetched
        """
        if self._style_json is None:
            assert self._style_url is not None
            self._set_style(json.dumps(self._get(self._style_url)))
        assert self._style_json is not None
        return self._style_json

    def name(self) -> str:
        """Return the name of the tile provider, including the style version

        Returns:
            str: name of tile provider
        """
        if self._version_hash is None:
            return self._name
        return f"{self._name}-{self._version_hash}"

    def attribution(self) -> typing.Optional[str]:
        """Return the attribution of the tile provider

        Returns:
            typing.Optional[str]: attribution of tile provider if available
        """
        if self._attribution is None and self._style_json is None:
            self.style()
        return self._attribution

    def tile_size(self) -> int:  # type: ignore[override]
        """Return the tile size

        Returns:
            int: tile size
        """
        return self._tile_size

    @staticmethod
    def is_vector() -> bool:
        """Return whether this provider needs a basemap backend

        Returns:
            bool: always True
        """
        return True

    def url(self, zoom: int, x: int, y: int) -> typing.Optional[str]:
        """Vector providers serve no raster tiles

        Parameters:
            zoom (int): zoom for static map
            x (int): x value of center for the static map
            y (int): y value of center for the static map

        Returns:
            typing.Optional[str]: always None
        """
        return None


def openfreemap(style: str = "liberty", max_zoom: int = 20) -> VectorTileProvider:
    """Return an OpenFreeMap vector tile provider

    OpenFreeMap needs no api key and imposes no request limits, but
    attribution is mandatory.

    Parameters:
        style (str): one of liberty, bright, positron, dark, fiord
        max_zoom (int): maximum zoom

    Returns:
        VectorTileProvider: provider for the given style
    """
    return VectorTileProvider(
        f"openfreemap-{style}",
        style_url=f"https://tiles.openfreemap.org/styles/{style}",
        max_zoom=max_zoom,
    )


# pylint: disable=invalid-name
tile_provider_OpenFreeMapLiberty = openfreemap("liberty")
tile_provider_OpenFreeMapBright = openfreemap("bright")
tile_provider_OpenFreeMapPositron = openfreemap("positron")
tile_provider_OpenFreeMapDark = openfreemap("dark")
tile_provider_OpenFreeMapFiord = openfreemap("fiord")

default_vector_tile_providers = {
    "openfreemap-liberty": tile_provider_OpenFreeMapLiberty,
    "openfreemap-bright": tile_provider_OpenFreeMapBright,
    "openfreemap-positron": tile_provider_OpenFreeMapPositron,
    "openfreemap-dark": tile_provider_OpenFreeMapDark,
    "openfreemap-fiord": tile_provider_OpenFreeMapFiord,
}
