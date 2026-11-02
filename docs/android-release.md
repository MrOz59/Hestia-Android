# Releasing Hestia Android

One workflow, [`Hestia Android Nightly`](../.github/workflows/nightly.yml), builds
every channel. The branch that is pushed decides what it publishes:

| Branch | Builds | Publishes |
| --- | --- | --- |
| `moonlight-noir` | Hestia Nightly (`com.mroz59.hestia.nightly`) | prerelease `v<base>-nightly.<run>` |
| `release/<month>-<year>-rc<n>` | Hestia Nightly | prerelease `<month>-<year>-rc<n>` |
| `release/v<major>.<minor>.<patch>` | Hestia (`com.mroz59.hestia`) | latest release `v<major>.<minor>.<patch>` |
| any other branch | Hestia Nightly, temporary test key | nothing (workflow artifacts only) |

`release/*` branches are trusted maintainer branches: like the default branch,
their builds are signed with the persistent `HESTIA_NIGHTLY_*` key.

## Cutting a stable release

1. Check that `moonlight-noir` has everything the release should contain and
   that its latest nightly works.
2. Optionally add `docs/v<version>-notes.md` (for example `docs/v0.7.0-notes.md`)
   with the release text. Without it, the release gets a standard text with the
   install instructions and a link to the changes since the previous stable
   release. The text can also be edited on GitHub after publication.
3. Create the branch `release/v<version>` from `moonlight-noir`:
   - **On github.com, also from a phone:** open the repository, tap the branch
     selector that shows `moonlight-noir`, type `release/v0.7.0` and choose
     **Create branch release/v0.7.0 from moonlight-noir**.
   - **From a checkout:** `git push origin moonlight-noir:refs/heads/release/v0.7.0`
4. The workflow builds stable Hestia, runs the JVM tests, verifies every APK
   (package, version, signature, TV launcher, codec) and publishes
   **Hestia Android 0.7.0** as the latest release, tagged `v0.7.0`, with:
   - `Hestia-Android-nonRoot-universal.apk` and the four ABI-specific APKs;
   - `SIGNING_CERT_SHA256.txt`, `RELEASE_MANIFEST.json` and `SHA256SUMS.txt`.

The publisher refuses to:

- publish without the persistent signing key;
- replace a tag or release that already exists. Release the next version
  instead;
- publish a commit that is no longer the branch's head. Pushing again to the
  branch starts a newer run, and that run publishes.

### Dry run

A version with a suffix, such as `release/v0.7.0-test`, builds and signs the
stable APKs exactly like a release and stops there. Download them from the run's
`Hestia-Android-stable-<run>` artifact. Delete the branch afterwards.

## Versions and identity

- `versionName` is the version from the branch name, without a suffix.
- `versionCode` is `100000 +` the workflow's run number, as for nightlies. Both
  are built by this workflow, so every stable release has a higher version code
  than the previous one. Do not move stable releases to another workflow file:
  its run number would start again from 1.
- Stable Hestia is a separate app from Hestia Nightly, with its own package,
  paired PCs and settings. Both are signed with the same persistent key, but
  their packages differ, so neither ever updates the other.
- The app's built-in Obtainium link looks for APKs whose name contains
  `nonRoot` and reads the version from the `v<version>` tag, which is why the
  stable APKs are named `Hestia-Android-nonRoot-*.apk`.

## Release candidates

Push `release/<month>-<year>-rc<n>` (for example `release/november-2026-rc1`)
with its notes in `docs/<month>-<year>-rc<n>-notes.md`. The candidate is the
signed nightly build of that commit, published as a prerelease with
`RC_MANIFEST.json`.
