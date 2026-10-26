# Hestia Android — October 2026 RC2

This candidate combines the Android TV interface, LAN discovery fixes and arm64
PyroWave decoder in the same APK.

## Changes since RC1

- Automatic TV layouts and remote navigation for Android TV, Google TV and
  compatible Fire TV devices, including visible selection, toolbar focus, manual
  host addition, local setup help and Menu/long-press OK context menus.
- Hestia launcher banner; phones and tablets keep their existing browsing UI.
- More resilient LAN discovery and corrected manual IPv6 address parsing.
- Advanced settings sections can be collapsed again with Show fewer options.
- Public APKs are no longer debuggable. RC publication requires persistent
  signing, verifies a shared certificate and checks that arm64 includes the
  PyroWave runtime and JNI decoder.

## Downloads and updates

Choose the non-root APK for your device's Android ABI. Most current devices use
`arm64-v8a`; some TV boxes need `armeabi-v7a` because their Android OS is 32-bit.
Root variants remain available for legacy rooted devices.

The RC keeps the Nightly package IDs and increasing Nightly version code. It
installs alongside stable Hestia, Artemis and Moonlight. **RC1 used a temporary
test certificate, so migrating to this permanent certificate may require
uninstalling the old Nightly/RC1 first. Back up your settings/profiles before
uninstalling.** Subsequent updates signed with the same permanent key can update
in place. The embedded version and exact source are recorded in `RC_MANIFEST.json`.

The same APK supports phones, tablets and Android-based TVs. Samsung Tizen and LG
webOS cannot run it directly; use a compatible Android device.

PyroWave is an explicit SDR option only on `arm64-v8a` with a compatible Vulkan
device and a fast LAN. Other ABIs retain their normal MediaCodec paths. Use the
existing codecs for HDR. The Android PyroWave path is not zero-copy.

## Testing and known limits

Please test automatic LAN discovery, manual IPv4/IPv6, pairing, connection/resume,
controllers, stylus events and TV remote navigation. Verify clean installation
and future updates with the persistent certificate. Report any installation
warning with its exact text, filename and hash; the Play Protect report (#16)
is still under investigation and is not claimed fixed.

CI verifies build/tests, TV and phone launcher metadata, non-debuggable APKs,
signatures/certificate consistency and arm64 PyroWave/JNI packaging. Real TV
decoder/HDMI behavior, phone GPU output and network discovery on the reporter's
LAN still require hardware testing.

Hermes RC3 is the recommended companion for its Gamescope/Wine shutdown cleanup.
Hermes-KMS RC1 and Hestia desktop RC1 remain compatible. Include component build
versions, device/Android, GPU/driver/kernel, codec and logs when reporting issues.

Support is also available on the new [Discord server](https://discord.gg/M5dYFuhjqP).
Responses may take time because the server is new, the community is small and
time zones differ.
