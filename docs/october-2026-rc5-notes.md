# Hestia Android — October 2026 RC5

RC5 shows how Hermes serves each stream when it connects, and sends a Hermes diagnostic report straight from the PC menu. It pairs with Hermes October RC7, which provides both.

## Changes since RC4

- **Stream info when a stream connects.** For a few seconds, an overlay at the top of the stream says how Hermes serves it: what it captures, the stream's size, rate and codec, the encoder and the GPU it encodes on, and the network latency. If Hermes' capture check found a problem and the stream went ahead anyway (`ignore_encoder_probe_failure` on the host), the overlay names the problem instead. The overlay takes no touches, so input keeps reaching the stream.
- **Send diagnostic report.** Long-press a paired, online Hermes host and choose **Send diagnostic report**. Hestia fetches the host's report and opens the share sheet, to save it, mail it or attach it to an issue. The report names clients and their addresses: read it before posting it publicly.
- Both need Hermes October RC7 or newer. With an older Hermes, or another host, nothing is shown, and the report option says the host gave no report.

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

Please check the stream info overlay when a stream connects (and that touch and controller input reach the stream while it shows), Send diagnostic report from the PC menu, and, as before, pairing/retry, discovery, connection/disconnection/reconnection, universal APK installation on phones and TVs, settings expansion/collapse with a remote, and controller/touch/stylus input where supported.

This is a prerelease. Automated tests do not replace device testing.

Support is also available on our new [Discord server](https://discord.gg/M5dYFuhjqP). Responses may take time because the server is new, the community is small and time zones differ.

Thanks to PunkUnity for the stream info and the diagnostic report in this candidate.
