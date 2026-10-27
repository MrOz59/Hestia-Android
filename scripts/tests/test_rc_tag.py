import copy
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
from urllib.error import HTTPError


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("rc_tag", ROOT / "scripts/prepare-rc-tag.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
SOURCE = "a" * 40


class CandidateTagTest(unittest.TestCase):
    def setup_api(self, tag="october-2026-rc3", old=module.WITHDRAWN_RC3, release=None):
        values = {
            f"git/ref/heads/release/{tag}": {"object": {"sha": SOURCE}},
            f"releases/tags/{tag}": release,
            f"git/ref/tags/{tag}": {"object": {"type": "commit", "sha": old}} if old else None,
            f"compare/{module.PHONE_TESTED_FIX}...{SOURCE}": {
                "status": "ahead", "merge_base_commit": {"sha": module.PHONE_TESTED_FIX}},
        }
        mutations = []

        def api(method, path):
            if method == "DELETE":
                mutations.append(path)
                return None
            return copy.deepcopy(values[path])

        return values, mutations, api

    def test_only_known_withdrawn_rc3_is_removed(self):
        _, mutations, api = self.setup_api()
        module.prepare(api, "october-2026-rc3", SOURCE)
        self.assertEqual(["git/refs/tags/october-2026-rc3"], mutations)

    def test_fresh_candidate_does_not_mutate_tags(self):
        _, mutations, api = self.setup_api("october-2026-rc4", old=None)
        module.prepare(api, "october-2026-rc4", SOURCE)
        self.assertEqual([], mutations)

    def test_existing_release_or_different_tag_never_gets_replaced(self):
        for args in ({"release": {"id": 1}}, {"old": "b" * 40}, {"tag": "october-2026-rc2"}):
            with self.subTest(args=args):
                _, mutations, api = self.setup_api(**args)
                with self.assertRaises(RuntimeError):
                    module.prepare(api, args.get("tag", "october-2026-rc3"), SOURCE)
                self.assertEqual([], mutations)

    def test_branch_move_and_missing_phone_fix_refuse_replacement(self):
        for path, value in (
            ("git/ref/heads/release/october-2026-rc3", {"object": {"sha": "b" * 40}}),
            (f"compare/{module.PHONE_TESTED_FIX}...{SOURCE}", {"status": "diverged"}),
        ):
            values, mutations, api = self.setup_api()
            values[path] = value
            with self.assertRaises(RuntimeError):
                module.prepare(api, "october-2026-rc3", SOURCE)
            self.assertEqual([], mutations)

    def test_lease_change_before_deletion_refuses_replacement(self):
        _, mutations, api = self.setup_api()
        reads = 0

        def racing_api(method, path):
            nonlocal reads
            if path == "git/ref/tags/october-2026-rc3":
                reads += 1
                if reads == 2:
                    return {"object": {"type": "commit", "sha": "b" * 40}}
            return api(method, path)

        with self.assertRaises(RuntimeError):
            module.prepare(racing_api, "october-2026-rc3", SOURCE)
        self.assertEqual([], mutations)

    @patch.dict("os.environ", {"GITHUB_REPOSITORY": "MrOz59/Hestia-Android", "GH_TOKEN": "test-only"})
    def test_only_http_404_is_treated_as_missing(self):
        for code in (401, 403, 429, 500):
            with self.subTest(code=code), patch.object(module, "urlopen", side_effect=HTTPError(
                    "https://api.github.com/", code, "Test", {}, None)):
                with self.assertRaises(RuntimeError):
                    module.github_api("GET", "releases/tags/october-2026-rc3")
        with patch.object(module, "urlopen", side_effect=HTTPError(
                "https://api.github.com/", 404, "Missing", {}, None)):
            self.assertIsNone(module.github_api("GET", "releases/tags/october-2026-rc3"))


if __name__ == "__main__":
    unittest.main()
