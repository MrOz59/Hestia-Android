# Hestia Android on TV

Hestia uses the same APK and package ID on phones, tablets and Android-based TVs.
There is no separate TV edition or TV-only build flavor. The APK selects its TV
browsing interface automatically from Android TV/Google TV UI mode, TV/Leanback
system features, or the Fire TV system feature. A large tablet or an external
monitor alone does not activate the TV interface.

## Install

1. Download **Hestia-Android-nightly-universal.apk**, the standard non-root APK
   for phones and TVs. It includes 32-bit and 64-bit ARM plus x86 libraries.
   Smaller ABI-specific APKs remain available. If using those, select the
   Android system ABI, not the CPU specification; some 64-bit CPUs run 32-bit
   Android and need `armeabi-v7a`.
2. Install the APK using the device's supported sideloading method. Hestia appears
   in the TV launcher with its Hestia banner.
3. Connect the TV and Hermes PC to the same LAN. Select the PC and enter the
   displayed pairing PIN in Hermes. If discovery fails, select **Add PC Manually**
   and enter the PC's LAN address.

For installation errors, see [TV package compatibility and diagnosis](android-tv-installation.md).
OpenGL ES 3.0 is optional; unsupported 3D modes fall back to normal streaming.

The normal Android minimum remains Android 5.0 (API 21). Codec, HDR, controller,
and performance support depend on the TV's firmware and decoder hardware.
Samsung Tizen and LG webOS cannot run this APK directly; use a compatible external
Android TV/Google TV/Fire TV device for those TVs.

## Remote navigation

- Use the D-pad to move and OK to select a PC or game.
- Hold OK or press Menu on a selected tile for its existing context menu.
- Use Up from the first grid row to reach the toolbar (or Hermes host status).
- Settings, manual host addition, help and profiles are accessible from the TV
  toolbar. Help opens locally instead of requiring a TV browser.
- Use a supported gamepad or keyboard/mouse during streaming. The remote's
  browsing shortcuts do not remap game input.

## Validation

JVM tests cover TV detection, phone/tablet layout selection, launcher declarations,
optional touchscreen/Leanback features, TV layout inflation, focus targets, empty
host lists and the remote Menu shortcut. CI also checks the metadata in built APKs.

Before declaring a release TV-tested, check on real Android TV/Google TV hardware
and Fire TV: launcher appearance; first launch with no hosts; manual entry with
the TV keyboard; pairing; D-pad navigation; long-press OK and Menu; host status;
profile editing; starting/stopping a stream; reconnect; controller input; and
codec/resolution/HDR modes supported by the device. Automated tests do not certify
decoder performance, HDMI behavior or TV firmware compatibility.
