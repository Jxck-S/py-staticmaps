"""py-staticmaps - basemap backends for vector tile rendering"""

# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import json
import subprocess
import sys
import typing
from abc import ABC, abstractmethod

# MapLibre GL defines zoom against 512px tiles (world = 512 * 2**z), while the
# XYZ/raster convention used throughout py-staticmaps uses 256px tiles
# (world = 256 * 2**z). Verified empirically against pymgl: the world fits a
# 512px image at zoom 0 and a 1024px image at zoom 1.
#
# Testing this at 256px is misleading, because zoom clamps at 0 and reports 0
# where it would need -1.
MAPLIBRE_ZOOM_OFFSET = -1

_PROBE_TIMEOUT = 60


class BasemapBackend(ABC):
    """Renders a whole basemap image from a MapLibre style.

    The seam sits at whole-image level rather than inside the per-tile loop
    because label collision detection needs the entire viewport; rendering
    tile by tile would clip and duplicate labels at every tile boundary.
    """

    @abstractmethod
    def render(
        self,
        style: str,
        width: int,
        height: int,
        zoom: float,
        longitude: float,
        latitude: float,
        ratio: float = 1.0,
    ) -> bytes:
        """Render a basemap to PNG bytes

        Parameters:
            style (str): MapLibre GL style as a json-encoded string
            width (int): width of the image in pixels
            height (int): height of the image in pixels
            zoom (float): zoom in the XYZ/256px convention used by this library
            longitude (float): center longitude
            latitude (float): center latitude
            ratio (float): pixel ratio of the output

        Returns:
            bytes: PNG image data
        """

    @staticmethod
    @abstractmethod
    def name() -> str:
        """Return the name of the backend

        Returns:
            str: name of the backend
        """


class PyMGLBackend(BasemapBackend):
    """Basemap backend using MapLibre Native via pymgl.

    pymgl bundles the MapLibre Native C++ engine, so output is that of the
    reference implementation: all layer types including labels, sprites and
    fill patterns.

    It renders on the GPU, but does not require GPU hardware. On a headless
    or GPU-less Linux host it works through Mesa's llvmpipe software
    rasterizer::

        apt-get install -y libegl1 libgl1-mesa-dri xvfb
        export LIBGL_ALWAYS_SOFTWARE=1
        xvfb-run -a --server-args="-screen 0 1024x768x24 -ac +render -noreset" python script.py

    macOS renders through Metal and needs no xvfb. Without a usable GL stack
    the process *segfaults* rather than raising, which is why availability is
    probed in a subprocess; see is_available().
    """

    @staticmethod
    def name() -> str:
        """Return the name of the backend

        Returns:
            str: name of the backend
        """
        return "pymgl"

    def render(
        self,
        style: str,
        width: int,
        height: int,
        zoom: float,
        longitude: float,
        latitude: float,
        ratio: float = 1.0,
    ) -> bytes:
        """Render a basemap to PNG bytes

        Parameters:
            style (str): MapLibre GL style as a json-encoded string
            width (int): width of the image in pixels
            height (int): height of the image in pixels
            zoom (float): zoom in the XYZ/256px convention used by this library
            longitude (float): center longitude
            latitude (float): center latitude
            ratio (float): pixel ratio of the output

        Returns:
            bytes: PNG image data

        Raises:
            RuntimeError: raises a runtime error if pymgl is not installed
        """
        try:
            from pymgl import Map  # pylint: disable=import-outside-toplevel
        except ImportError as e:
            raise RuntimeError(
                'You need to install the "pymgl" module to render vector tiles. '
                "See the vector tiles documentation for headless/GPU-less setup."
            ) from e

        gl_zoom = max(0.0, zoom + MAPLIBRE_ZOOM_OFFSET)

        # pymgl segfaults if an instance is reassigned without being deleted,
        # so the instance is dropped explicitly rather than left to the gc.
        map_instance = Map(style, width, height, ratio, longitude, latitude, gl_zoom)
        try:
            return typing.cast(bytes, map_instance.renderPNG())
        finally:
            del map_instance

    @staticmethod
    def is_available() -> bool:
        """Check whether pymgl can actually render in this environment

        The check runs in a subprocess: a missing or broken GL stack makes
        pymgl segfault, which cannot be caught in-process.

        Returns:
            bool: True if a trivial render succeeds
        """
        style = json.dumps(
            {
                "version": 8,
                "sources": {},
                "layers": [{"id": "bg", "type": "background", "paint": {"background-color": "#ffffff"}}],
            }
        )
        code = (
            "from pymgl import Map;"
            f"m=Map({style!r},64,64,1,0,0,0);"
            "d=m.renderPNG();"
            "del m;"
            "raise SystemExit(0 if d else 1)"
        )
        try:
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                timeout=_PROBE_TIMEOUT,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            return False
        return result.returncode == 0


_backend_cache: typing.Dict[str, typing.Optional[BasemapBackend]] = {}


def select_backend(name: str = "auto") -> BasemapBackend:
    """Return a basemap backend

    Parameters:
        name (str): "auto" or "pymgl"

    Returns:
        BasemapBackend: the selected backend

    Raises:
        ValueError: raises a value error if the backend name is unknown
        RuntimeError: raises a runtime error if no backend is usable
    """
    if name not in ("auto", "pymgl"):
        raise ValueError(f'unknown basemap backend "{name}"')

    if name in _backend_cache:
        cached = _backend_cache[name]
        if cached is not None:
            return cached

    if name == "pymgl":
        backend: BasemapBackend = PyMGLBackend()
        _backend_cache[name] = backend
        return backend

    if PyMGLBackend.is_available():
        backend = PyMGLBackend()
        _backend_cache[name] = backend
        return backend

    raise RuntimeError(
        "No usable basemap backend. Install pymgl with "
        '"pip install py-staticmaps[pymgl]". On a headless Linux host also install '
        "libegl1, libgl1-mesa-dri and xvfb, set LIBGL_ALWAYS_SOFTWARE=1, and run "
        "under xvfb-run."
    )
