"""py-staticmaps - Test that the generated documentation sections expand"""

# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import pathlib
import re

SUMMARY = pathlib.Path("docs/SUMMARY.md")


def test_generated_sections_use_the_directory_form() -> None:
    """literate-nav descends into a section's own SUMMARY.md only when the
    navigation points at the directory. Pointing at index.md instead makes the
    section a single leaf page, and every generated page under it becomes
    unreachable from the navigation while still building and returning 200.
    """
    nav = SUMMARY.read_text(encoding="utf-8")
    for section in ("examples", "reference"):
        assert f"({section}/)" in nav, f"{section} must be linked as a directory, not a page"
        assert f"({section}/index.md)" not in nav
