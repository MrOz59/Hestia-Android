#!/usr/bin/env python3
"""Keep candidates immutable, with one approved exception for withdrawn RC3."""
import json
import os
import re
from urllib.error import HTTPError
from urllib.request import Request, urlopen


WITHDRAWN_RC3 = "d15d300a1895dbf2570844adf4a79ab921a6e09d"
PHONE_TESTED_FIX = "67db06d1be89ab72ff6223162aa4ebff613ab9d8"


def prepare(api, tag, source):
    if not re.fullmatch(r"october-2026-rc[0-9]+", tag) or not re.fullmatch(r"[0-9a-f]{40}", source):
        raise RuntimeError("Invalid candidate tag or source")
    branch_path = f"git/ref/heads/release/{tag}"
    release_path = f"releases/tags/{tag}"
    tag_path = f"git/ref/tags/{tag}"
    branch = api("GET", branch_path)
    if branch is None or branch["object"]["sha"] != source:
        raise RuntimeError("Candidate branch moved; refusing stale publication")
    if api("GET", release_path) is not None:
        raise RuntimeError("Candidate release already exists; choose the next RC")
    previous = api("GET", tag_path)
    if previous is None:
        return
    expected = {"type": "commit", "sha": WITHDRAWN_RC3}
    if tag != "october-2026-rc3" or any(previous["object"].get(k) != v for k, v in expected.items()):
        raise RuntimeError("Existing candidate tag is not the explicitly withdrawn RC3")
    comparison = api("GET", f"compare/{PHONE_TESTED_FIX}...{source}")
    if (comparison.get("status") not in ("ahead", "identical") or
            comparison.get("merge_base_commit", {}).get("sha") != PHONE_TESTED_FIX):
        raise RuntimeError("Replacement RC3 does not contain the phone-tested pairing fix")
    # Recheck the branch, release and tag immediately before the narrow delete.
    if (api("GET", branch_path)["object"]["sha"] != source or
            api("GET", release_path) is not None or api("GET", tag_path) != previous):
        raise RuntimeError("Candidate state changed; refusing tag replacement")
    api("DELETE", f"git/refs/tags/{tag}")
    print("Removed only the withdrawn RC3 tag; publication will create it at the fixed source")


def github_api(method, path):
    request = Request(
        f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/{path}",
        method=method,
        headers={"Authorization": f"Bearer {os.environ['GH_TOKEN']}",
                 "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28"},
    )
    try:
        with urlopen(request, timeout=30) as response:
            body = response.read()
            return json.loads(body) if body else None
    except HTTPError as error:
        if method == "GET" and error.code == 404:
            return None
        # Authorization/network failures must never be mistaken for absence.
        raise RuntimeError(f"GitHub {method} {path}: HTTP {error.code}") from None


if __name__ == "__main__":
    prepare(github_api, os.environ["RC_TAG"], os.environ["GITHUB_SHA"])
