"""Fetch the fixed external Codeflaws archive without extracting or executing it.

The source programs are not redistributed in this artifact. The URL is linked
by the upstream project; an archive with different bytes is always rejected.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
import urllib.request

ARCHIVE_SHA256 = "2673fc16fa05590c5c1171f5b633594713ae9207346a3d0ba4c4d8b2eea82b11"
ARCHIVE_BYTES = 265695532
UPSTREAM_URL = "https://www.comp.nus.edu.sg/~release/codeflaws/codeflaws.tar.gz"
ARTIFACT = Path(__file__).resolve().parents[1]


def verify(path):
    if path.stat().st_size != ARCHIVE_BYTES:
        raise ValueError("archive byte count differs from the fixed snapshot")
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    if h.hexdigest() != ARCHIVE_SHA256:
        raise ValueError("archive SHA256 differs from the fixed snapshot")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--url", default=UPSTREAM_URL)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    if output == ARTIFACT or ARTIFACT in output.parents:
        raise ValueError("keep the external archive outside the distributable artifact")
    if output.exists():
        verify(output)
    elif args.verify_only:
        raise FileNotFoundError(output)
    else:
        if not args.url.startswith(("https://", "http://")):
            raise ValueError("an upstream HTTP(S) URL is required")
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=output.parent, prefix="codeflaws-download-", suffix=".part", delete=False) as stream:
                temporary = Path(stream.name)
                request = urllib.request.Request(args.url, headers={"User-Agent": "RepairSeal-artifact-fetch/1"})
                total = 0
                with urllib.request.urlopen(request, timeout=60) as response:
                    for block in iter(lambda: response.read(1048576), b""):
                        total += len(block)
                        if total > ARCHIVE_BYTES:
                            raise ValueError("download exceeds the fixed snapshot size")
                        stream.write(block)
            verify(temporary)
            # An exclusive hard-link commit does not overwrite an archive created
            # concurrently. Both names are on the same destination filesystem.
            os.link(temporary, output)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
    print(json.dumps({"path": str(output), "bytes": ARCHIVE_BYTES, "sha256": ARCHIVE_SHA256,
                      "verified": True, "extracted": False, "executed": False}))


if __name__ == "__main__":
    main()
