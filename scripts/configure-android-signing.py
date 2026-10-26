#!/usr/bin/env python3
"""Create a local backed-up signing key and upload it to GitHub Actions Secrets.

Run on the maintainer's trusted computer with Java keytool and authenticated gh.
Private key material is never printed or committed. Retain the output directory.
"""
import argparse
import base64
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default="MrOz59/Hestia-Android")
    parser.add_argument("--directory", type=Path, required=True,
                        help="Private backup directory outside the repository")
    parser.add_argument("--generate-only", action="store_true",
                        help="Create/validate the local key without contacting GitHub")
    args = parser.parse_args()
    for command in (("keytool",) if args.generate_only else ("keytool", "gh")):
        if not shutil.which(command):
            parser.error(f"Install {command} first")
    if not args.generate_only:
        subprocess.run(["gh", "auth", "status"], check=True, stdout=subprocess.DEVNULL)
    directory = args.directory.expanduser().resolve()
    checkout = Path(__file__).resolve().parents[1]
    if directory == checkout or checkout in directory.parents:
        parser.error("Choose a backup directory outside the repository")
    # Refuse to generate a second key accidentally. A partial secret upload can
    # be retried using the same directory and its original identity.
    os.umask(0o077)
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    directory.chmod(0o700)
    keystore = directory / "hestia-nightly.p12"
    metadata = directory / "signing.json"
    if keystore.exists() != metadata.exists():
        parser.error("Incomplete backup: retain and repair it; do not replace the signing key")
    if not keystore.exists():
        if any(directory.iterdir()):
            parser.error("Use an empty private backup directory")
        identity = {"alias": "hestia", "password": secrets.token_urlsafe(40)}
        env = dict(os.environ, HESTIA_KEY_PASSWORD=identity["password"])
        subprocess.run([
            "keytool", "-genkeypair", "-noprompt", "-storetype", "PKCS12",
            "-keystore", str(keystore), "-alias", identity["alias"],
            "-storepass:env", "HESTIA_KEY_PASSWORD", "-keypass:env", "HESTIA_KEY_PASSWORD",
            "-keyalg", "RSA", "-keysize", "3072", "-sigalg", "SHA256withRSA",
            "-validity", "36500", "-dname", "CN=Hestia Android, O=MrOz59",
        ], check=True, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        metadata.write_text(json.dumps(identity) + "\n")
    identity = json.loads(metadata.read_text())
    env = dict(os.environ, HESTIA_KEY_PASSWORD=identity["password"])
    subprocess.run(["keytool", "-list", "-keystore", str(keystore),
                    "-storepass:env", "HESTIA_KEY_PASSWORD", "-alias", identity["alias"]],
                   check=True, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if args.generate_only:
        print("Local signing identity is ready for encrypted backup.")
        return
    values = {
        "HESTIA_NIGHTLY_KEYSTORE_BASE64": base64.b64encode(keystore.read_bytes()).decode(),
        "HESTIA_NIGHTLY_STORE_PASSWORD": identity["password"],
        "HESTIA_NIGHTLY_KEY_ALIAS": identity["alias"],
        "HESTIA_NIGHTLY_KEY_PASSWORD": identity["password"],
    }
    for name, value in values.items():
        subprocess.run(["gh", "secret", "set", name, "--repo", args.repository],
                       input=value.encode(), check=True, stdout=subprocess.DEVNULL)
        print(f"Configured {name}")
    print(f"Keep a secure backup of {directory}. Reuse this directory for retries.")


if __name__ == "__main__":
    main()
