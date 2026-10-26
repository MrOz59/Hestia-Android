#!/usr/bin/env python3
"""Encrypt/restore a signing backup; pass its password through BACKUP_PASSWORD."""
import argparse
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile

FILES = ("hestia-nightly.p12", "signing.json")


def backup(operation, directory, encrypted, password):
    if len(password) < 32:
        raise ValueError("Use a backup password with at least 32 characters")
    os.umask(0o077)
    directory = Path(directory)
    encrypted = Path(encrypted)
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    directory.chmod(0o700)
    with tempfile.TemporaryDirectory() as temporary:
        archive = Path(temporary) / "signing.tar.gz"
        home = Path(temporary) / "gnupg"
        home.mkdir(mode=0o700)
        command = ["gpg", "--homedir", str(home), "--no-symkey-cache", "--batch", "--yes",
                   "--pinentry-mode", "loopback", "--passphrase-fd", "0"]
        try:
            if operation == "encrypt":
                encrypted.parent.mkdir(parents=True, exist_ok=True)
                with tarfile.open(archive, "w:gz") as tar:
                    for name in FILES:
                        source = directory / name
                        if not source.is_file() or source.is_symlink():
                            raise ValueError("Signing backup must contain regular key and metadata files")
                        tar.add(source, arcname=name)
                subprocess.run(command + ["--symmetric", "--cipher-algo", "AES256", "--output",
                                          str(encrypted), str(archive)], input=password.encode(),
                               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            else:
                if any(directory.iterdir()):
                    raise ValueError("Restore into an empty directory")
                subprocess.run(command + ["--decrypt", "--output", str(archive), str(encrypted)],
                               input=password.encode(), check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                with tarfile.open(archive, "r:gz") as tar:
                    members = tar.getmembers()
                    if sorted(member.name for member in members) != sorted(FILES) or not all(
                            member.isfile() and member.size <= 65536 for member in members):
                        raise ValueError("Unexpected backup contents")
                    for member in members:
                        (directory / member.name).write_bytes(tar.extractfile(member).read())
        finally:
            subprocess.run(["gpgconf", "--homedir", str(home), "--kill", "gpg-agent"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("encrypt", "decrypt"))
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--file", type=Path, required=True)
    args = parser.parse_args()
    backup(args.operation, args.directory, args.file, os.environ.get("BACKUP_PASSWORD", ""))
