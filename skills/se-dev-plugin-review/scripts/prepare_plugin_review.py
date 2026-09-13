#!/usr/bin/env python3
"""Prepare a PluginHub or MagnetarHub review from its PR URL."""

import argparse
from pathlib import Path

from _review_common import prepare


HUBS = {"StarCpt/PluginHub", "CometWorks/magnetar-hub"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pr_url", help="PluginHub or MagnetarHub GitHub PR URL")
    parser.add_argument("--output", type=Path, help="Review artifact directory")
    args = parser.parse_args()
    return prepare(args.pr_url, args.output, HUBS, "pulsar_magnetar")


if __name__ == "__main__":
    raise SystemExit(main())
