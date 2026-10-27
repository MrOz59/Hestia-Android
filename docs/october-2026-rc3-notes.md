# Hestia Android — October 2026 RC3 (reissued)

A streaming client for Android phones, tablets and TVs, with a universal APK
and fixes for interrupted or overlapping pairing attempts.

**This replaces the withdrawn RC3.** It includes the Android 14+ pairing crash
fix tested in nightly 67. The maintainer confirmed that the app starts, pairs
and connects successfully. If you downloaded the earlier RC3, download this new
APK again: it has a higher Android version code and the same signing key, so it
can update the old build without uninstalling.

## Which APK should I download?

**Choose `Hestia-Android-nightly-universal.apk` if you are unsure.** It includes
all four supported architectures and automatically uses the phone or TV
interface. You do not need a separate TV edition.

| APK file | Who should use it? |
| --- | --- |
| **`Hestia-Android-nightly-universal.apk` — Recommended** | **Phones, tablets, Android TV, Google TV and compatible Fire TV devices.** The easiest choice when you do not know your device's architecture. |
| `Hestia-Android-nightly-arm64-v8a.apk` | A smaller download for **64-bit ARM Android**, used by most current phones/tablets and some TVs. |
| `Hestia-Android-nightly-armeabi-v7a.apk` | A smaller download for **32-bit ARM Android**, common on older phones and many TV boxes/TVs. Some TVs have a 64-bit processor but still run 32-bit Android. |
| `Hestia-Android-nightly-x86.apk` | **32-bit Intel Android** devices or Android emulators configured for x86. |
| `Hestia-Android-nightly-x86_64.apk` | **64-bit x86 Android** devices or Android emulators configured for x86_64. This is still an Android app, not a Windows/Linux desktop installer. |

Each APK is a complete app: **install only one**. The four smaller downloads
have the same app features, subject to hardware support; use them only when you
know your Android architecture. **All downloads work without root.**

Requires **Android 5.0 or newer**. Samsung TVs running **Tizen** and LG TVs running
**webOS** need an external Android device; those TV systems cannot install APKs.
The APK is the client; your PC runs the streaming host, such as Hermes.

## Installing or updating

1. Download the **universal APK** above, or the smaller APK matching your Android
   architecture.
2. Open the APK on the Android phone, tablet or TV and allow installation from
   that download/file app if Android asks.
3. Open **Hestia Nightly**, add your PC, pair it and select an application to stream.

RC3 still appears as **Hestia Nightly** and can update RC2 and recent permanently
signed nightlies in place when its version is newer. RC1 and old nightlies used
another signing key and may require backing up settings/profiles before
uninstalling that older app. Hestia installs alongside Artemis and Moonlight.

`SHA256SUMS.txt` contains download checksums, `SIGNING_CERT_SHA256.txt` identifies
the signing certificate, and `RC_MANIFEST.json` records the exact source/version.
They are verification files, not apps to install.

## What changed since RC2?

- **Pairing crash fixed:** Android 14+ network-discovery events arriving after
  discovery stops no longer crash the app when opening pairing. Covered by
  Android 14/16 regression tests and confirmed on the maintainer's phone.
- **Universal APK:** one recommended file for phones and TVs, including 32/64-bit
  ARM and x86. Four architecture-specific APKs remain as smaller alternatives.
- **TV compatibility:** normal 2D streaming no longer requires OpenGL ES 3.0.
  Devices without it fall back to 2D when a 3D mode is selected, and 2D startup
  avoids initializing the 3D/OpenCV renderer.
- **Pairing recovery:** prevent overlapping attempts, cancel incomplete sessions
  after errors, avoid replaying state-changing challenges and retry only the
  final HTTPS confirmation after transient failures. Abandoned PIN waits time
  out after three minutes. PIN, signature and certificate checks stay enforced.
- **Permissions:** remove unwanted phone/storage permissions and the keyboard
  accessibility service. Native shortcut capture is available on Android 16.1+;
  older devices may keep system-reserved shortcuts locally.
- **Release checks:** persistent signing, package/version checks, phone/TV
  launcher metadata, permission checks, four universal ABIs and arm64 PyroWave.

## Using PyroWave

Choose **Settings → Advanced Settings → Change codec settings →
PyroWave (Experimental, SDR LAN)**. In Portuguese, the codec menu may still be
labelled **Mudar configurações do HEVC**.

Enable PyroWave in **Hermes too**, disable HDR and begin with **720p at 60 FPS**
on a fast local network. PyroWave requires **64-bit ARM Android and a compatible
Vulkan device**. It is included in the universal APK's arm64 path and the
`arm64-v8a` APK. Normal codecs remain available on all four architectures.
Android PyroWave is experimental and is not zero-copy.

## Pairing fix on the PC and testing

For the full pairing recovery fix, also use a Hermes build containing
[the companion server update, PR #77](https://github.com/MrOz59/Hermes/pull/77).
It repairs stale-session replacement, cancellation and session lifetime bugs.
Existing **Hermes RC3 remains compatible**, but that release does not include
this additional server fix. Hermes-KMS RC1 and Hestia desktop RC1 remain compatible.

Please test installation/update, TV remote navigation, discovery/manual IPv4 and
IPv6, first-attempt PIN/OTP pairing, app-list access, streaming and reconnecting.
Controllers, stylus input, normal codecs/HDR and PyroWave SDR also need testing
where supported.

Startup, pairing and connection were confirmed by the maintainer using the
fixed nightly 67. Broader phone/tablet testing, stylus behavior and physical TV
decoder/HDMI behavior still need validation. Sensitive permissions were removed, but **Play Protect acceptance is
not guaranteed** by build or signing checks. If installation or pairing fails,
include the exact error, APK/version, device/Android, host version and relevant
logs. Never include PINs, passphrases or private keys.

Support is available on [Discord](https://discord.gg/M5dYFuhjqP). Responses may take
time because the server is new, the community is small and time zones differ.
