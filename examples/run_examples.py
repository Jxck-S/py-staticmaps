#!/usr/bin/env python

"""py-staticmaps - run every example and collect its output

The example list lives in this directory and nowhere else: this script
discovers examples/*.py rather than repeating their names, so the Makefile,
CI and the documentation cannot drift apart.

An example that cannot run here is skipped with its reason rather than
failing the run, because several need an optional dependency or an api key
that is not always present.
"""

# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import argparse
import json
import os
import pathlib
import subprocess
import sys
import typing

HERE = pathlib.Path(__file__).parent.resolve()
BUILD = HERE / "build"

# examples that need an argument; everything else is run with none
ARGUMENTS: typing.Dict[str, typing.List[str]] = {
    "draw_gpx.py": ["running.gpx"],
}

# this script is not itself an example
EXCLUDED = {"run_examples.py"}

OUTPUT_SUFFIXES = (".png", ".svg")

# records which files each example produced, so the docs need not guess
MANIFEST = "manifest.json"


def discover() -> typing.List[pathlib.Path]:
    """Return every example script in this directory

    Returns:
        typing.List[pathlib.Path]: example scripts, sorted by name
    """
    return sorted(p for p in HERE.glob("*.py") if p.name not in EXCLUDED)


def run(script: pathlib.Path, timeout: int) -> typing.Tuple[bool, str, typing.List[str]]:
    """Run one example and move whatever it produced into build/

    Parameters:
        script (pathlib.Path): example to run
        timeout (int): seconds to allow

    Returns:
        tuple: whether it succeeded, a one-line reason when it did not, and
        the names of the files it produced
    """
    before = {p for p in HERE.iterdir() if p.suffix in OUTPUT_SUFFIXES}
    env = dict(os.environ, PYTHONPATH=str(HERE.parent))
    try:
        result = subprocess.run(
            [sys.executable, script.name, *ARGUMENTS.get(script.name, [])],
            cwd=HERE,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return False, f"timed out after {timeout}s", []
    except OSError as e:
        return False, f"{type(e).__name__}: {e}", []

    produced = sorted(p for p in HERE.iterdir() if p.suffix in OUTPUT_SUFFIXES and p not in before)
    names = [p.name for p in produced]
    for path in produced:
        path.replace(BUILD / path.name)

    if result.returncode != 0:
        reason = (result.stderr or result.stdout or "").strip().splitlines()
        return False, reason[-1][:100] if reason else f"exit {result.returncode}", names
    if not produced:
        # an example that prints why it is skipping rather than failing
        note = (result.stdout or "").strip().splitlines()
        return False, note[-1][:100] if note else "produced no output", names
    return True, f"{len(produced)} file(s)", names


def main() -> int:
    """Run every example

    Returns:
        int: process exit code
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=int, default=300, help="seconds allowed per example")
    parser.add_argument("--strict", action="store_true", help="fail if any example is skipped")
    args = parser.parse_args()

    BUILD.mkdir(exist_ok=True)
    scripts = discover()
    print(f"running {len(scripts)} examples into {BUILD}\n")

    skipped = []
    manifest: typing.Dict[str, typing.List[str]] = {}
    for script in scripts:
        ok, note, names = run(script, args.timeout)
        print(f"  {'ok  ' if ok else 'SKIP'}  {script.name:24} {note}")
        manifest[script.name] = names
        if not ok:
            skipped.append(script.name)

    with open(BUILD / MANIFEST, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)

    print(f"\n{len(scripts) - len(skipped)}/{len(scripts)} produced output")
    if skipped:
        print(f"skipped: {', '.join(skipped)}")
    return 1 if (skipped and args.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
