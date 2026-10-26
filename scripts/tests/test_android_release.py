import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


class AndroidReleaseTest(unittest.TestCase):
    def test_manifest_requires_all_apks_and_records_public_provenance(self):
        with tempfile.TemporaryDirectory() as temporary:
            payload = Path(temporary)
            (payload / 'SIGNING_CERT_SHA256.txt').write_text('a' * 64 + '\n')
            env = dict(os.environ, RC_TAG='october-2026-rc2', GITHUB_SHA='b' * 40,
                       BUILD_VERSION='20.2.6-nightly.50', GITHUB_REPOSITORY='MrOz59/Hestia-Android',
                       GITHUB_RUN_ID='123')
            command = [sys.executable, str(ROOT / 'scripts/write-rc-manifest.py'), str(payload)]
            self.assertNotEqual(0, subprocess.run(command, env=env, capture_output=True).returncode)
            for index in range(8):
                (payload / f'fixture-{index}.apk').write_bytes(bytes([index]))
            subprocess.run(command, env=env, check=True)
            manifest = json.loads((payload / 'RC_MANIFEST.json').read_text())
            self.assertEqual(8, len(manifest['payload_sha256']))
            self.assertEqual('persistent', manifest['signing'])
            self.assertEqual('a' * 64, manifest['certificate_sha256'])
            self.assertEqual('arm64-v8a', manifest['pyrowave_abi'])

    @unittest.skipUnless(shutil.which('keytool'), 'Java keytool required')
    def test_setup_retains_key_across_retries_and_passes_secrets_only_on_stdin(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            binary = root / 'bin'
            binary.mkdir()
            gh = binary / 'gh'
            gh.write_text('#!' + sys.executable + '\n' + '''
import json, os, sys
from pathlib import Path
if sys.argv[1:] == ['auth', 'status']:
    raise SystemExit(0)
assert sys.argv[1:3] == ['secret', 'set']
assert len(sys.argv) == 6 and sys.argv[4] == '--repo'
path = Path(os.environ['TEST_SECRET_CAPTURE'])
data = json.loads(path.read_text()) if path.exists() else {}
data[sys.argv[3]] = sys.stdin.read()
path.write_text(json.dumps(data))
''')
            gh.chmod(0o700)
            capture = root / 'captured.json'
            env = dict(os.environ, PATH=str(binary) + os.pathsep + os.environ['PATH'],
                       TEST_SECRET_CAPTURE=str(capture))
            backup = root / 'backup'
            command = [sys.executable, str(ROOT / 'scripts/configure-android-signing.py'),
                       '--directory', str(backup)]
            first = subprocess.run(command, env=env, check=True, capture_output=True, text=True)
            original = (backup / 'hestia-nightly.p12').read_bytes()
            identity = json.loads((backup / 'signing.json').read_text())
            second = subprocess.run(command, env=env, check=True, capture_output=True, text=True)
            self.assertEqual(original, (backup / 'hestia-nightly.p12').read_bytes())
            values = json.loads(capture.read_text())
            self.assertEqual(4, len(values))
            self.assertEqual(identity['password'], values['HESTIA_NIGHTLY_STORE_PASSWORD'])
            for result in (first, second):
                self.assertNotIn(identity['password'], result.stdout + result.stderr)
                self.assertNotIn(values['HESTIA_NIGHTLY_KEYSTORE_BASE64'], result.stdout + result.stderr)
            self.assertEqual(0o700, backup.stat().st_mode & 0o777)


class SigningBackupTest(unittest.TestCase):
    def require_gpg_agent(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run(['gpg-connect-agent', '--homedir', temporary, '/bye'],
                                    capture_output=True, timeout=10)
            if result.returncode:
                if os.environ.get('GITHUB_ACTIONS') == 'true':
                    self.fail('The CI runner must support GnuPG agent operations')
                self.skipTest('This local sandbox does not allow GnuPG agent sockets; CI runs this check')
            subprocess.run(['gpgconf', '--homedir', temporary, '--kill', 'gpg-agent'],
                           capture_output=True, timeout=10)

    @unittest.skipUnless(shutil.which('gpg'), 'GnuPG required')
    def test_encrypted_backup_roundtrip_and_wrong_password_rejection(self):
        self.require_gpg_agent()
        import importlib.util
        specification = importlib.util.spec_from_file_location('signing_backup', ROOT / 'scripts/signing-backup.py')
        module = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'private'
            source.mkdir()
            key = b'test-private-key-bytes'
            metadata = b'{"alias":"hestia","password":"private-test-password"}'
            (source / 'hestia-nightly.p12').write_bytes(key)
            (source / 'signing.json').write_bytes(metadata)
            encrypted = root / 'backup.gpg'
            password = 'test-backup-password-' + 'a' * 32
            module.backup('encrypt', source, encrypted, password)
            self.assertNotIn(key, encrypted.read_bytes())
            self.assertNotIn(metadata, encrypted.read_bytes())
            with self.assertRaises(subprocess.CalledProcessError):
                module.backup('decrypt', root / 'wrong', encrypted, 'wrong-password-' + 'b' * 32)
            restored = root / 'restored'
            module.backup('decrypt', restored, encrypted, password)
            self.assertEqual(key, (restored / 'hestia-nightly.p12').read_bytes())
            self.assertEqual(metadata, (restored / 'signing.json').read_bytes())
            with self.assertRaises(ValueError):
                module.backup('decrypt', restored, encrypted, password)
            with self.assertRaises(ValueError):
                module.backup('encrypt', source, encrypted, 'too-short')

    @unittest.skipUnless(shutil.which('gpg'), 'GnuPG required')
    def test_restore_rejects_unexpected_archive_paths(self):
        self.require_gpg_agent()
        import importlib.util
        import io
        import tarfile
        specification = importlib.util.spec_from_file_location('signing_backup', ROOT / 'scripts/signing-backup.py')
        module = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / 'unexpected.tar.gz'
            with tarfile.open(archive, 'w:gz') as tar:
                member = tarfile.TarInfo('../outside')
                member.size = 1
                tar.addfile(member, io.BytesIO(b'x'))
            password = 'test-backup-password-' + 'a' * 32
            encrypted = root / 'unexpected.gpg'
            subprocess.run(['gpg', '--batch', '--yes', '--pinentry-mode', 'loopback',
                            '--passphrase-fd', '0', '--symmetric', '--cipher-algo', 'AES256',
                            '--output', str(encrypted), str(archive)], input=password.encode(),
                           check=True, capture_output=True)
            with self.assertRaises(ValueError):
                module.backup('decrypt', root / 'restored', encrypted, password)
            self.assertFalse((root / 'outside').exists())

    @unittest.skipUnless(shutil.which('keytool'), 'Java keytool required')
    def test_generate_only_does_not_contact_github(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            binary = root / 'bin'
            binary.mkdir()
            gh = binary / 'gh'
            gh.write_text('#!/bin/sh\nexit 99\n')
            gh.chmod(0o700)
            env = dict(os.environ, PATH=str(binary) + os.pathsep + os.environ['PATH'])
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/configure-android-signing.py'),
                                     '--directory', str(root / 'key'), '--generate-only'],
                                    env=env, capture_output=True, check=True, text=True)
            identity = json.loads((root / 'key/signing.json').read_text())
            self.assertNotIn(identity['password'], result.stdout + result.stderr)
            self.assertTrue((root / 'key/hestia-nightly.p12').is_file())


if __name__ == '__main__':
    unittest.main()
