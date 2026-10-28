# Hestia Android — October 2026 RC4

RC4 improves settings navigation and expands pairing regression coverage while retaining the universal phone/TV APK and the current discovery lifecycle improvements.

## Changes since RC3

- Keep settings category expansion and collapse rows in predictable positions.
- Restore D-pad focus when a settings category is collapsed and provide matching expansion/collapse arrows.
- Add coverage for an incorrect first PIN followed by a verified retry.

## Which APK should I install?

**For most people, install `Hestia-Android-nightly-universal.apk`.** The same APK supports Android phones, tablets and Android-based TVs, including 32-bit ARM TV systems. It includes all four CPU architectures.

The four smaller alternatives contain the same app for a single CPU architecture:

| Download | Choose it for |
| --- | --- |
| `…-universal.apk` | Recommended when unsure; phones, tablets and Android TVs |
| `…-arm64-v8a.apk` | Devices running 64-bit ARM Android |
| `…-armeabi-v7a.apk` | Devices running 32-bit ARM Android, including many TVs |
| `…-x86.apk` | Devices or emulators running 32-bit x86 Android |
| `…-x86_64.apk` | Devices or emulators running 64-bit x86 Android |

Select the architecture of the installed Android system, which may be 32-bit even when the processor supports 64-bit. Install only one APK; the ABI-specific files are optional alternatives to the universal download.

These are regular, non-root APKs. They do not require root, an accessibility service or global screen-reading access. Normal 2D streaming does not require OpenGL ES 3.0; that capability is optional for 3D modes.

## Compatibility and updates

- APKs use the persistent signing key. Keep the existing Hestia Android installation and install this candidate as an update.
- This build uses the Hestia nightly application identity and can coexist with Artemis, Moonlight and stable Hestia.
- PyroWave is included for arm64-v8a devices with compatible Vulkan support and a fast LAN. The existing codecs remain available on every architecture.
- Native shortcut capture is available on Android 16.1 and newer; older Android versions retain some system-reserved shortcuts.

`SIGNING_CERT_SHA256.txt`, `RC_MANIFEST.json` and `SHA256SUMS.txt` describe the certificate, exact source/build and payload checksums. They do not need to be installed.

## Testing and support

Please check pairing/retry, discovery, connection/disconnection/reconnection, universal APK installation on phones and TVs, settings expansion/collapse with a remote, and controller/touch/stylus input where supported.

This is a prerelease. Automated tests do not replace device testing.

Support is also available on our new [Discord server](https://discord.gg/M5dYFuhjqP). Responses may take time because the server is new, the community is small and time zones differ.
