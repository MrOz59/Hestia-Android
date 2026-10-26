# Hestia-Android — October 2026 release candidate 1

Coordinated RC for testing before the end-of-October stable release. This is a **prerelease**, not a stable release.

- Source commit: [`0ef14edfd152b4d220d3f2992c82c101e582ca44`](https://github.com/MrOz59/Hestia-Android/commit/0ef14edfd152b4d220d3f2992c82c101e582ca44)
- Validated build: [Actions run 40258250143](https://github.com/MrOz59/Hestia-Android/actions/runs/40258250143)
- Embedded build version: `20.2.6-nightly.32`

This is an immutable promotion of the exact successful CI artifacts. Package/APK bytes, embedded build versions, filenames and signatures are preserved; the shared `october-2026-rc1` tag identifies the coordinated candidate. `RC_MANIFEST.json` records each source/build/artifact identity, and `SHA256SUMS` covers all attached payload files.

## Included

- The PyroWave-enabled build of PR #13, including both normal and root variants for four ABIs. **PyroWave itself is supported only on arm64-v8a with a compatible Vulkan device**; other ABIs keep their existing MediaCodec paths.
- Select the ordinary `Hestia-Android-nightly-arm64-v8a.apk` on most current phones; root APKs are only for the legacy rooted-device variant.
- The APKs retain their Nightly identities, version `20.2.6-nightly.32` and original test signatures. They install separately from stable Hestia, Artemis and Moonlight. Updating another nightly signed with a different test key may require uninstalling that nightly first.
- The optional SDK build, JNI/runtime checks, both flavors, JVM tests and packet/loss regressions passed.

This promotes the feature-branch build that actually includes PyroWave. The newer default-branch nightly did not enable that SDK, so it was not used. PyroWave is opt-in, SDR 4:2:0, and this baseline reads decoded planes back to CPU memory before GLES upload; it is not zero-copy.

## Matching candidates

- [Hermes RC1](https://github.com/MrOz59/Hermes/releases/tag/october-2026-rc1) — `964c5fa24b4992f942a59142e82b3adee8214de9`
- [Hestia RC1](https://github.com/MrOz59/Hestia/releases/tag/october-2026-rc1) — `94a1bc58b510f7417bd208ed70cd22d2b89ed649`
- [Hestia-Android RC1](https://github.com/MrOz59/Hestia-Android/releases/tag/october-2026-rc1) — `0ef14edfd152b4d220d3f2992c82c101e582ca44`
- [Hermes-KMS RC1](https://github.com/MrOz59/Hermes-KMS/releases/tag/october-2026-rc1) — `8c8aa0812783437c91e6d65ff8073fdbe57068b2`

## Remaining validation

Real-host AMD capture/encode, desktop and Android streaming, SDR/HDR, disconnect/reconnect, concurrent isolated Gamescope sessions, DS4/optional DualSense, private audio/microphone and upgrade/rollback checks remain part of RC testing. Passing CI does not record those hardware tests as completed. PyroWave HDR is outside the supported candidate path; use the existing codecs for HDR.

When reporting a problem, include this RC tag, component build version, GPU/driver/kernel, client device and codec, and logs from both ends.
