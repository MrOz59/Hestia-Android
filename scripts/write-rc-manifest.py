#!/usr/bin/env python3
"""Record the exact candidate inputs without including signing secrets."""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

payload = Path(sys.argv[1])
apks = sorted(payload.glob("*.apk"))
expected_apks = {
    f"Hestia-Android-nightly-{abi}.apk"
    for abi in ("universal", "arm64-v8a", "armeabi-v7a", "x86", "x86_64")
}
if {p.name for p in apks} != expected_apks:
    raise SystemExit("Expected the universal APK and four ABI-specific APKs")
certificate = (payload / "SIGNING_CERT_SHA256.txt").read_text().strip()
if not re.fullmatch(r"[a-fA-F0-9]{64}", certificate):
    raise SystemExit("Invalid signing certificate fingerprint")
manifest = {
    "tag": os.environ["RC_TAG"],
    "source_commit": os.environ["GITHUB_SHA"],
    "build_version": os.environ["BUILD_VERSION"],
    "workflow_run": f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}",
    "signing": "persistent",
    "certificate_sha256": certificate,
    "pyrowave_abi": "arm64-v8a",
    "recommended_apk": "Hestia-Android-nightly-universal.apk",
    "validation": ["jvm-tests", "phone-tv-launchers", "non-debuggable", "v1-v2-signatures", "same-certificate-all-apks", "arm64-codec-and-jni"],
    "payload_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in apks},
}
(payload / "RC_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
