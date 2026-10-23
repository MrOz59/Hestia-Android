# Hestia Android nightlies

The workflow [`Hestia Android Nightly`](../.github/workflows/nightly.yml) compiles **both non-root and root** Android builds for every push to any branch, including the push created by merging a pull request.

- Every successful build is downloadable as a GitHub Actions artifact, retained for 14 days.
- **Only successful pushes to `moonlight-noir`** publish a GitHub **pre-release** under [Releases](https://github.com/MrOz59/Hestia-Android/releases). Feature-branch pushes build but do not publish public releases.
- A nightly release has its own immutable tag, e.g. `v20.2.6-nightly.15`, so release watchers can recognize new versions.
- The release contains 4 APKs for each flavor (`arm64-v8a`, `armeabi-v7a`, `x86`, `x86_64`), along with `SHA256SUMS.txt`.
- Android JVM tests must pass before publication. APK package identities and monotonically increasing Android version codes are verified with `aapt`.
- The workflow can be invoked manually from the Actions tab after it has been merged to the default branch.

## What to install

For nearly all modern Android phones and tablets, choose:

```
Hestia-Android-nightly-arm64-v8a.apk
```

The `*-root-*` APKs are for the separate, legacy rooted flavor; most users should avoid them.

The regular nightly ID is `com.mroz59.hestia.nightly`, separate from stable Hestia (`com.mroz59.hestia`) and Artemis. The root nightly ID is `com.mroz59.hestia.root.nightly`. These applications store pairing certificates and preferences independently.

## Persistent signing (recommended before asking others to test)

Android requires updates of an installed package to be signed with the **same key**. A GitHub-hosted runner's default debug keystore is regenerated, so without a persistent signing key, a new nightly **may require uninstalling the old one**, losing the nightly's locally stored settings and pairing.

Set these four **Actions repository secrets** on `MrOz59/Hestia-Android`:

| Secret | Contents |
| --- | --- |
| `HESTIA_NIGHTLY_KEYSTORE_BASE64` | Base64 (single line) of a dedicated PKCS#12/JKS keystore |
| `HESTIA_NIGHTLY_STORE_PASSWORD` | Keystore password |
| `HESTIA_NIGHTLY_KEY_ALIAS` | Name of the signing key |
| `HESTIA_NIGHTLY_KEY_PASSWORD` | Private key password |

Example: generate a **new dedicated nightly-only key** locally. Never use a production signing key for CI builds.

```sh
keytool -genkeypair -v -keystore hestia-nightly.p12 -storetype PKCS12 \
  -alias hestia-nightly -keyalg RSA -keysize 3072 -validity 10000
base64 -w0 hestia-nightly.p12 | gh secret set HESTIA_NIGHTLY_KEYSTORE_BASE64 -R MrOz59/Hestia-Android
gh secret set HESTIA_NIGHTLY_STORE_PASSWORD -R MrOz59/Hestia-Android
gh secret set HESTIA_NIGHTLY_KEY_ALIAS -R MrOz59/Hestia-Android --body hestia-nightly
gh secret set HESTIA_NIGHTLY_KEY_PASSWORD -R MrOz59/Hestia-Android
```

For the password commands, `gh secret set` reads the value from standard input, so paste the password and finish input when prompted. Do **not** commit `.p12` / `.jks` files to the repository. Store an offline backup of the key: losing it means Android cannot update previously signed nightly installs.

Set **all four** secrets together; the workflow fails if only some are present, rather than unexpectedly switching to another key. With all four configured, Gradle signs the nightly build with the persistent key. Before that, it uses the Android debug key and marks the release accordingly.

**One-time migration:** Nightlies installed before persistent signing is configured will still need to be uninstalled once before installing the first permanently signed build.

## Release policy

- Every push on any branch runs the build; a pull request does not directly create a public release.
- Each merged/default-branch build creates one prerelease, with a fresh numeric nightly version.
- Nightlies do **not** replace stable releases, and are intentionally debuggable for development.
- Version numbers derive from the workflow run number (Android `versionCode = 100000 + run_number`). Avoid renaming/recreating the workflow without reviewing version-code monotonicity.
- To follow nightlies in Obtainium, point it at this repository and **enable prereleases**; filter for `Hestia-Android-nightly-arm64-v8a.apk` on typical devices. The nightly tag is `v<base version>-nightly.<run number>`.
