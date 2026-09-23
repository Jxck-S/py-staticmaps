"""py-staticmaps - meta

GITHUB_URL identifies this client to tile servers, through the user agent the
downloader sends, so it names the repository actually making the requests.
VERSION is a PEP 440 local version on top of the 0.5.0 this was forked from:
the public part says which upstream release the code descends from, the local
part says whose fork it is. Without it both report 0.5.0 and nothing in a log
or in pip list can tell them apart. Bump the local segment for a release of
this fork, and the public part when it picks up a new upstream.
"""

# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

GITHUB_URL = "https://github.com/Jxck-S/py-staticmaps"
LIB_NAME = "py-staticmaps"
VERSION = "0.5.0+jxck.1"
