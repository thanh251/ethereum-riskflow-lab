from __future__ import annotations

import argparse

import _bootstrap  # noqa: F401
from riskflow.server import serve


parser = argparse.ArgumentParser()
parser.add_argument("--host", default=None)
parser.add_argument("--port", type=int, default=None)
args = parser.parse_args()
serve(args.host, args.port)

