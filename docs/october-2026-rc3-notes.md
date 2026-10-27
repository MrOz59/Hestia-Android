# Hestia Android — October 2026 RC3

RC3 adds a universal phone/TV APK and improves recovery from interrupted or
overlapping pairing attempts.

## Changes since RC2

- **One recommended download:** `Hestia-Android-nightly-universal.apk` includes
  ARM 32/64-bit and x86 32/64-bit libraries. Four smaller architecture-specific
  APKs are the only alternative downloads.
- **TV installation:** OpenGL ES 3.0 is optional. Normal 2D streaming uses
  SurfaceView; devices without GLES 3.0 fall back to 2D if a 3D mode is selected.
  Ordinary 2D startup avoids initializing the 3D/OpenCV renderer.
- **Pairing:** prevent overlapping attempts, cancel incomplete sessions after
  errors, avoid automatically replaying state-changing challenges and tolerate
  transient failures during the final HTTPS confirmation. PIN, signature and
  certificate checks remain enforced.
- **Public APK permissions:** remove unwanted phone/storage permissions and
  the keyboard accessibility service. Native shortcut capture is available on
  Android 16.1+; older devices may keep system-reserved shortcuts locally.
- Persistent signing and APK checks cover package identity, versions, TV
  launcher metadata, permissions, all four universal ABIs and arm64 PyroWave.

## Download and update

Use **`Hestia-Android-nightly-universal.apk`** on Android phones, tablets, Android
TV, Google TV and compatible Fire TV devices. Android 5.0/API 21 or newer is
required. Samsung Tizen and LG webOS cannot install Android APKs directly.

RC3 retains the Nightly package identity and permanent signing certificate used
by RC2 and recent nightlies. It updates them in place when its version code is
newer. RC1 and old nightlies signed with a temporary key may require backing up
settings/profiles and uninstalling that older app before migration. The exact
source, embedded version and payload hashes are in `RC_MANIFEST.json`.

PyroWave is included on the universal APK's arm64 path and the arm64-specific
APK. It requires a compatible Vulkan device, HDR disabled and a fast LAN. Enable
it in both Hermes and Hestia's codec settings; begin with 720p60. Other codecs
remain available on every architecture. The Android PyroWave path is not
zero-copy.

## Please test

- Clean installation/update on phones and TVs, including 32-bit Android TV.
- PIN and OTP pairing, first-attempt success, app-list access, connection,
  disconnect and reconnect. Include the visible error and both sides' logs if
  repeated attempts are still needed.
- LAN discovery/manual IPv4 and IPv6, TV remote navigation, controllers and
  stylus input, plus normal codecs/HDR and PyroWave SDR where supported.

The pairing changes address reproducible failure paths; confirmation on the
reporter's hardware/network is still pending. TV decoder/HDMI behavior and phone
GPU output also require physical-device testing. Sensitive permissions were
removed, but acceptance by Google Play Protect must be confirmed on devices and
is not guaranteed by the build or signing checks.

For the full pairing recovery fix, also use a Hermes build containing
[the companion server update, PR #77](https://github.com/MrOz59/Hermes/pull/77).
It repairs stale-session replacement, cancellation and session lifetime bugs.
Existing Hermes RC3 remains compatible, but that immutable release does not
include the server fix. Hermes-KMS RC1 and Hestia desktop RC1 remain compatible.
Include component versions, device/Android, GPU/driver, codec and logs when
reporting issues.

Support is also available on the new [Discord server](https://discord.gg/M5dYFuhjqP).
Responses may take time because the server is new, the community is small and
time zones differ.
