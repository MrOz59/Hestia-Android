# Persistent Android signing and installation reports

Public APKs are non-debuggable. Every nightly includes the arm64 PyroWave runtime,
TV UI and normal MediaCodec paths. CI verifies APK signatures, a shared certificate
across the universal APK and all eight ABI/flavor APKs, launcher metadata and the arm64 codec/JNI entry points.

## Setup without a PC

Use the [phone/browser-only setup](android-signing-web.md). It generates the key
in a manually started default-branch workflow, configures the four signing Secrets
and starts RC2. The recovery backup is encrypted before upload.

## Maintainer setup

The existing four `HESTIA_NIGHTLY_*` repository secrets are reused for nightlies
and RCs. The private key is exposed only on the default branch and the controlled
`release/october-2026-rc*` branches; feature and PR builds use temporary test keys. Feature builds also exercise the
custom keystore path and verify the APK signer against that temporary certificate,
without exposing the permanent key.
Creating or updating those release branches is a trusted maintainer operation.

On a trusted computer with Java `keytool` and authenticated GitHub CLI, run:

```bash
python3 scripts/configure-android-signing.py --directory "$HOME/hestia-signing-backup"
```

This generates an encrypted PKCS12 key outside the checkout, keeps its credentials
in the private backup directory and uploads the four secrets through `gh` stdin.
It never prints private material. Back up that directory securely. Re-running with
the same directory reuses the key; do not generate replacement keys for updates.
If a signing identity already exists, configure its original keystore/passwords
instead of creating another one.

After configuring the secrets, rerun the latest workflow on
`release/october-2026-rc2`. The RC publisher refuses temporary signing, verifies the
branch still matches the tested commit, and refuses to replace existing RC tags.
Successful builds with missing secrets remain available as test artifacts; they
are not published as RCs.

## Transition from RC1

RC1 retained the Nightly package IDs and a runner-local test certificate. The new
persistent certificate cannot update an APK signed with that previous key. Export
profiles/settings as available before uninstalling the old Nightly/RC1, then
install the persistently signed RC2. Once migrated, future builds using this same
key and a higher version code can update in place. Stable Hestia, Artemis and
Moonlight use separate application IDs and can remain installed.

Compare the APK certificate with `SIGNING_CERT_SHA256.txt` from the release.
`RC_MANIFEST.json` records the source, workflow, certificate and APK hashes.

## Play Protect report (#16)

The report currently has no exact warning, APK filename/hash or screenshot. A
signature mismatch, an unrecognized application prompt and a Play Protect harmful
app classification are different outcomes. Persistent signing and removing the
debuggable flag improve the release process but do not prove the report's cause
or guarantee that Google's classification will change.

For the next report, collect the exact warning text/screenshot, Android/device
version, downloaded filename, SHA-256, certificate fingerprint and whether this
is a clean install or update. Keep the issue open until the outcome is verified.
If Google incorrectly classifies the final signed artifact, use the official
[app verification appeal](https://support.google.com/googleplay/android-developer/answer/2992033).
Do not use disabling Play Protect as the installation instructions.

Android's [app signing documentation](https://developer.android.com/studio/publish/app-signing)
explains why updates require the same signing identity and why the private key
must be retained.
