#!/usr/bin/env python

"""py-staticmaps - raster @2x (HiDPI) tiles example

A provider serving "@2x" tiles declares tile_size=512: the tile covers the
same ground as a 256px one but carries four times the pixels. Keep the zoom,
double the requested size, and the result covers the identical area with
twice the pixel density -- which is what a HiDPI display or a print job
wants.

This is the raster counterpart of set_pixel_ratio() for vector providers.
Both trade geographic coverage for density in exactly the same way, so

    render_cairo(size=(1080, 1080))                          # 512px tiles
    render_cairo(logical_size=(540, 540), pixel_ratio=2)     # vector

cover the same ground and produce the same 1080x1080 image.

Needs a free CARTO api key in API_KEY_CARTO; see carto.com/basemaps/apikey
"""

# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import os

import staticmaps

KEY = os.environ.get("API_KEY_CARTO")
ZOOM = 15
CENTER = staticmaps.create_latlng(37.7990, -122.4000)

ferry = staticmaps.create_latlng(37.7955, -122.3937)
coit = staticmaps.create_latlng(37.8024, -122.4058)


def build(provider: staticmaps.TileProvider, density: int) -> staticmaps.Context:
    """Build a context whose objects are scaled with the tile density

    Parameters:
        provider (TileProvider): raster tile provider
        density (int): 1 for 256px tiles, 2 for "@2x" 512px tiles

    Returns:
        Context: context ready to render
    """
    context = staticmaps.Context()
    context.set_tile_provider(provider)
    context.add_object(staticmaps.Line([ferry, coit], color=staticmaps.GREEN, width=3 * density))
    context.add_object(staticmaps.Marker(ferry, color=staticmaps.RED, size=10 * density))
    context.add_object(staticmaps.Marker(coit, color=staticmaps.BLUE, size=10 * density))
    context.set_center(CENTER)
    context.set_zoom(ZOOM)
    return context


if KEY is None:
    print("Set API_KEY_CARTO to run this example; see carto.com/basemaps/apikey")
elif not staticmaps.cairo_is_supported():
    print('You need to install the "cairo" module to run this example.')
else:
    for name, scale, size in (("carto-voyager", 1, 540), ("carto-voyager-2x", 2, 1080)):
        tile_provider = staticmaps.default_tile_providers[name]
        tile_provider.set_api_key(KEY)
        image = build(tile_provider, scale).render_cairo(size=(size, size))
        filename = f"tile_size_2x.{scale}x.cairo.png"
        image.write_to_png(filename)
        print(f"{filename}: {image.get_width()}x{image.get_height()} px, tile_size={tile_provider.tile_size()}")
