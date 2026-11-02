#!/usr/bin/env python3
"""Record the exact candidate or release inputs without including signing secrets.

Release candidates publish the nightly APKs (Hestia-Android-nightly-*.apk) with
RC_MANIFEST.json. Stable releases pass --apk-prefix Hestia-Android-nonRoot and
--output RELEASE_MANIFEST.json, and set RELEASE_TAG instead of RC_TAG.
"""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path

ABIS = ("universal", "arm64-v8a", "armeabi-v7a", "x86", "x86_64")

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("payload", type=Path)
parser.add_argument("--apk-prefix", default="Hestia-Android-nightly")
parser.add_argument("--output", default="RC_MANIFEST.json")
args = parser.parse_args()

payload = args.payload
apks = sorted(payload.glob("*.apk"))
expected_apks = {f"{args.apk_prefix}-{abi}.apk" for abi in ABIS}
if {p.name for p in apks} != expected_apks:
    raise SystemExit("Expected the universal APK and four ABI-specific APKs")
certificate = (payload / "SIGNING_CERT_SHA256.txt").read_text().strip()
if not re.fullmatch(r"[a-fA-F0-9]{64}", certificate):
    raise SystemExit("Invalid signing certificate fingerprint")
manifest = {
    "tag": os.environ.get("RELEASE_TAG") or os.environ["RC_TAG"],
    "source_commit": os.environ["GITHUB_SHA"],
    "build_version": os.environ["BUILD_VERSION"],
    "workflow_run": f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}",
    "signing": "persistent",
    "certificate_sha256": certificate,
    "pyrowave_abi": "arm64-v8a",
    "recommended_apk": f"{args.apk_prefix}-universal.apk",
    "validation": ["jvm-tests", "phone-tv-launchers", "non-debuggable", "v1-v2-signatures", "same-certificate-all-apks", "arm64-codec-and-jni"],
    "payload_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in apks},
}
(payload / args.output).write_text(json.dumps(manifest, indent=2) + "\n")
