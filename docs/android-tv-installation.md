# Installing Hestia on Android TVs

Use **Hestia-Android-nightly-universal.apk** from the newest
[release](https://github.com/MrOz59/Hestia-Android/releases). It is the standard
non-root app for both phones and Android-based TVs, and includes ARM 32-bit,
ARM 64-bit, x86 and x86_64 libraries. Android selects a supported ABI at install
time. It is larger than an individual ABI download but avoids needing to guess
the TV's architecture.

Android version and CPU model alone do not establish which ABIs an Android
system exposes. In particular, a 64-bit-capable CPU can run a 32-bit system.
If using the smaller APKs, select `armeabi-v7a` for ARM 32-bit Android and
`arm64-v8a` for a system supporting ARM 64-bit. The root variants are legacy
builds, not a TV edition; ordinary Android TVs should use the non-root app.

The normal app declares minimum Android API 21 (Android 5.0), has no maximum API
limit, and includes a Leanback launcher, a TV banner and optional touchscreen
and microphone features. Android TV 12 meets the declared Android-version
requirement. This does not by itself verify every model's hardware or firmware.

OpenGL ES 3.0 is now optional. Normal 2D streaming uses SurfaceView and does not
initialize the OpenCV/3D renderer. If a 3D mode is selected on a device reporting
only GLES 2.0 or no graphics capability, Hestia falls back to normal streaming
and displays a message, without rewriting the saved rendering preference.
PyroWave remains available only on the universal APK's arm64 path or the arm64
split, with a compatible Vulkan GPU; it is not required to install or use normal
streaming on a 32-bit TV.

## If installation is rejected

The reporter's TCL Android TV 12 message, "App isn't compatible with your phone",
does not identify the package-manager error. The word "phone" alone does not
show that the APK is phone-only. Obtain:

- Exact TV model and Android version.
- Exact APK filename and release version.
- Whether an earlier Hestia package is installed, and which version.
- The full installer message or, when available, the `adb install -r` error.

With ADB already configured, `adb shell getprop ro.product.cpu.abilist` reports
the supported ABIs. `INSTALL_FAILED_NO_MATCHING_ABIS`, a signature mismatch,
version downgrade, missing platform library and a Play Protect block require
different fixes; do not infer the cause solely from the generic UI message.

The first universal build retains the permanent Nightly certificate and package
ID and has a higher version code than previous nightlies. It can update RC2 and
other permanently signed nightlies in place. Older ephemeral-key test builds may
require backing up profiles and uninstalling once before installing the new app.

CI validates every split plus the standard universal APK, all four native cores
inside the universal APK, shared signatures, phone/TV launcher metadata and
non-debuggable flags. Android 12 framework tests exercise GLES 2.0 and unknown-GPU
fallback. Real TCL installation, decoder output and remote behavior still need
device validation; the packaging fixes are not proof of the original cause.

References:

- [Android ABIs](https://developer.android.com/ndk/guides/abis)
- [Android TV hardware requirements](https://developer.android.com/training/tv/get-started/hardware)
- [Android platform version requirements](https://developer.android.com/guide/topics/manifest/uses-sdk-element)
