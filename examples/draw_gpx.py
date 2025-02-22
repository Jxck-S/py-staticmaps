#!/usr/bin/env python

"""py-staticmaps - Example Draw GPX"""
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import sys

import gpxpy  # type: ignore

import staticmaps

context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_ArcGISWorldImagery)

with open(sys.argv[1], "r", encoding="utf-8") as file:
    gpx = gpxpy.parse(file)

for track in gpx.tracks:
    for segment in track.segments:
        line = [staticmaps.create_latlng(p.latitude, p.longitude) for p in segment.points]
        context.add_object(staticmaps.Line(line))

# add an image marker to the first track point
for p in gpx.walk(only_points=True):
    pos = staticmaps.create_latlng(p.latitude, p.longitude)
    marker = staticmaps.ImageMarker(pos, "start.png", origin_x=27, origin_y=35)
    context.add_object(marker)
    break

# render png via pillow
image = context.render_pillow(800, 500)
image.save("draw_gpx.pillow.png")

# render png via cairo
if staticmaps.cairo_is_supported():
    image = context.render_cairo(800, 500)
    image.write_to_png("draw_gpx.cairo.png")

# render svg
svg_image = context.render_svg(800, 500)
with open("draw_gpx.svg", "w", encoding="utf-8") as f:
    svg_image.write(f, pretty=True)

# render svg - tight boundaries
context.set_tighten_to_bounds(True)
svg_image = context.render_svg(800, 500)
with open("draw_gpx.tight.svg", "w", encoding="utf-8") as f:
    svg_image.write(f, pretty=True)
